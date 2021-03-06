import sublime, sublime_plugin
import gspatch, margo, gscommon as gs, gslint
from os.path import dirname, relpath, basename
import re

DOMAIN = 'GsPalette'
last_import_path = {}

class Loc(object):
	def __init__(self, fn, row, col=0):
		self.fn = fn
		self.row = row
		self.col = col

class GsPaletteCommand(sublime_plugin.WindowCommand):
	def is_enabled(self):
		return bool(gs.active_valid_go_view(self.window))

	def run(self, palette='auto', direct=False):
		if not hasattr(self, 'items'):
			self.items = []
			self.bookmarks = []
			self.last_activate_palette = ''
			self.requires_margo = ['declarations', 'imports']
			self.palettes = {
				'declarations': self.palette_declarations,
				'imports': self.palette_imports,
				'errors': self.palette_errors,
			}

		if palette == 'jump_back':
			self.jump_back()
		elif palette == 'jump_to_imports':
			self.jump_to_imports()
		else:
			self.show_palette(palette, direct)

	def show_palette(self, palette, direct=False):
		view = gs.active_valid_go_view(self.window)
		if not view:
			return

		palette = palette.lower().strip()
		if palette == 'auto':
			palette = self.last_activate_palette
		elif palette == 'main':
			palette = ''

		pcb = None
		if palette:
			pcb = self.palettes.get(palette)
			if pcb:
				self.last_activate_palette = palette
			else:
				gs.notice(DOMAIN, 'Invalid palette `%s`' % palette)
				palette = ''

		if not direct and len(self.bookmarks) > 0:
			loc = self.bookmarks[-1]
			line = 'line %d' % (loc.row + 1)
			if view.file_name() == loc.fn:
				fn = ''
			else:
				fn = relpath(loc.fn, dirname(loc.fn))
				if fn.startswith('..'):
					fn = loc.fn
				fn = '%s ' % fn
			self.add_item(u'\u2190 Go Back (%s%s)' % (fn, line), self.jump_back, None)

		if not direct and palette:
			self.add_item(u'@%s \u21B5' % palette.title(), self.show_palette, 'main')

		li1 = len(self.items)
		if pcb:
			pcb(view, direct)

		if not direct:
			for k in sorted(self.palettes.keys()):
				if k:
					if k != palette:
						ttl = '@' + k.title()
						if k == 'errors':
							fr = gslint.ref(view.file_name())
							if not fr or len(fr.reports) == 0:
								continue
							ttl = '%s (%d)' % (ttl, len(fr.reports))
						itm = ttl
						self.add_item(itm, self.show_palette, k)

		items = []
		actions = {}
		for tup in self.items:
			item, action, args = tup
			actions[len(items)] = (action, args)
			items.append(item)
		self.items = []

		def on_done(i):
			action, args = actions.get(i, (None, None))
			if i >= 0 and action:
				action(args)
		self.window.show_quick_panel(items, on_done)

	def add_item(self, item, action=None, args=None):
		self.items.append((item, action, args))

	def log_bookmark(self, view, loc):
		bks = self.bookmarks
		if len(bks) == 0 or (bks[-1].row != loc.row and bks[-1].fn != view.file_name()):
			bks.append(loc)

	def goto(self, loc):
		self.window.open_file('%s:%d:%d' % (loc.fn, loc.row+1, loc.col+1), sublime.ENCODED_POSITION)

	def jump_to_imports(self):
		view = gs.active_valid_go_view()
		if not view:
			return

		last_import = last_import_path.get(view.file_name())
		r = None
		if last_import:
			offset = len(last_import) + 2
			last_import = re.escape(last_import)
			pat = '(?s)import.*?(?:"%s"|`%s`)' % (last_import, last_import)
			r = view.find(pat, 0)

		if not r:
			offset = 1
			pat = '(?s)import.*?["`]'
			r = view.find(pat, 0)

		if not r:
			gs.notice(DOMAIN, "cannot find import declarations")
			return

		pt = r.end() - offset
		row, col = view.rowcol(pt)
		loc = Loc(view.file_name(), row, col)
		self.jump_to((view, loc))

	def jump_back(self, _=None):
		if len(self.bookmarks) > 0:
			self.goto(self.bookmarks.pop())

	def palette_errors(self, view, direct=False):
		indent = '' if direct else '    '
		reps = {}
		fr = gslint.ref(view.file_name())
		if fr:
			reps = fr.reports.copy()
		for k in sorted(reps.keys()):
			r = reps[k]
			loc = Loc(view.file_name(), r.row, r.col)
			m = "%sline %d: %s" % (indent, r.row+1, r.msg)
			self.add_item(m, self.jump_to, (view, loc))

	def palette_imports(self, view, direct=False):
		indent = '' if direct else '    '
		im, err = margo.imports(
			view.file_name(),
			view.substr(sublime.Region(0, view.size())),
			True,
			[]
		)
		if err:
			gs.notice(DOMAIN, err)

		delete_imports = []
		add_imports = []
		imports = im.get('file_imports', [])
		for path in im.get('import_paths', []):
			skipAdd = False
			for i in imports:
				if i.get('path') == path:
					skipAdd = True
					name = i.get('name', '')
					if not name:
						name = basename(path)
					if name == path:
						delete_imports.append(('%sdelete: %s' % (indent, name), i))
					else:
						delete_imports.append(('%sdelete: %s ( %s )' % (indent, name, path), i))

			if not skipAdd:
				add_imports.append(('%s%s' % (indent, path), {'path': path, 'add': True}))
		for i in sorted(delete_imports):
			self.add_item(i[0], self.toggle_import, (view, i[1]))
		self.add_item(' --- ', self.show_palette, 'imports')
		for i in sorted(add_imports):
			self.add_item(i[0], self.toggle_import, (view, i[1]))

	def toggle_import(self, a):
		global last_import_path

		view, decl = a
		im, err = margo.imports(
			view.file_name(),
			view.substr(sublime.Region(0, view.size())),
			False,
			[decl]
		)
		if err:
			gs.notice(DOMAIN, err)
		else:
			src = im.get('src', '')
			size_ref = im.get('size_ref', 0)
			if src and size_ref > 0:
				dirty, err = gspatch.merge(view, size_ref, src)
				if err:
					gs.notice_undo(DOMAIN, err, view, dirty)
				elif dirty:
					if decl.get('add'):
						last_import_path[view.file_name()] = decl.get('path')
					else:
						last_import_path[view.file_name()] = ''
					gs.notice(DOMAIN, 'imports updated...')

	def jump_to(self, a):
		view, loc = a
		row, col = gs.rowcol(view)
		if loc.row != row:
			self.log_bookmark(view, Loc(view.file_name(), row, col))
		self.goto(loc)

	def palette_declarations(self, view, direct=False):
		indent = '' if direct else '    '
		decls, err = margo.declarations(
			view.file_name(),
			view.substr(sublime.Region(0, view.size()))
		)
		if err:
			gs.notice('GsDeclarations', err)
		decls.sort(key=lambda v: v['line'])
		for i, v in enumerate(decls):
			if v['name'] == '_':
				continue
			loc = Loc(v['filename'], v['line']-1, v['column']-1)
			prefix = u'%s%s \u00B7   ' % (indent, gs.CLASS_PREFIXES.get(v['kind'], ''))
			self.add_item(prefix+v['name'], self.jump_to, (view, loc))
