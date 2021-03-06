import time
from talon import Module, Context, actions, app, clip, cron, ui

mod = Module()
ctx = Context()

ctx.matches = r"""
app.bundle: com.microsoft.onenote.mac
"""

@ctx.action_class('edit')
class EditActions:
	def copy():
		serial_start = clip.serial()
		for attempt in range(10):
			actions.key("cmd-c")
			actions.sleep("100ms")
			if clip.serial() != serial_start:
				return

	def select_line(n: int=None):
		actions.key('cmd-a')
		actions.sleep('100ms')

@mod.action_class
class Actions:
	def onenote_focus():
		"""Bring OneNote to the front."""
		return actions.user.launch_or_focus_bundle('com.microsoft.onenote.mac')

	def onenote_now():
		"""Insert timestamped bullet list item into OneNote."""
		# XXX work around inability to focus and insert in a single action
		# XXX potentially related to https://github.com/talonvoice/talon/issues/305?
		if actions.user.onenote_focus():
			cron.after('200ms', lambda: actions.user.onenote_now())

	def onenote_checkbox():
		"""Insert indented checkbox into OneNote."""

	def onenote_heading_1():
		"""Insert a first-level heading into OneNote."""

	def onenote_hide_navigation():
		"""Hide the navigation panes."""

	def onenote_copy_link():
		"""Copy a link to the current paragraph in OneNote."""

	def onenote_go_progress():
		"""Go to the first section of the first notebook."""

	def onenote_go_recent(offset: int):
		"""Navigate to recent notes."""

def onenote_app():
	return ui.apps(bundle="com.microsoft.onenote.mac")[0]

def onenote_window():
	return next(window for window in onenote_app().windows() if window.doc)

@ctx.action_class('user')
class UserActions:
	# user.find_and_replace
	def find(text: str):
		actions.key("ctrl-g cmd-f")
		actions.sleep("100ms")
		actions.insert(text)

	def find_everywhere(text: str):
		actions.key("ctrl-g cmd-alt-f")
		actions.sleep("200ms")
		actions.insert(text)

	def find_next():     actions.key('cmd-g')
	def find_previous(): actions.key('cmd-shift-g')
	
	# not standard OneNote; approximate equivalents of AutoHotKey
	def onenote_heading_1():
		actions.key('ctrl-e enter')
		# custom shortcut for "Remove Tag"
		actions.key('cmd-alt-0')
		actions.key('shift-tab:5')
		# neither bullets nor numbering
		actions.key('cmd-. cmd-/ cmd-/')
		# outdent one more time as the above may indent
		actions.key('shift-tab')
		actions.key('cmd-alt-1')

	def onenote_checkbox(): actions.key('ctrl-e enter tab cmd-1 up ctrl-e')
	
	def onenote_hide_navigation():
		onenote = onenote_app()
		window = onenote_window()
		# hide the navigation pane(s) if necessary
		splitgroup = window.children.find_one(AXRole='AXSplitGroup', max_depth=0)
		group = splitgroup.children.find_one(AXRole='AXGroup', max_depth=0)
		try:
			checkbox = group.children.find_one(AXRole='AXCheckBox', AXValue=1, max_depth=0)
		except ui.UIErr:
			pass
		else:
			checkbox.perform('AXPress')
		# focus the note body if necessary
		for attempt in range(10):
			focused = onenote.focused_element
			if focused.AXRole == 'AXWindow' and focused.get('AXDocument'):
				actions.sleep('100ms')
				actions.key('tab')
				actions.sleep('100ms')
			else:
				return
		app.notify(body='Unable to focus note body', title='OneNote')

	def onenote_go_recent(offset: int):
		window = onenote_window()

		splitgroup = window.children.find_one(AXRole='AXSplitGroup', max_depth=0)
		group = splitgroup.children.find_one(AXRole='AXGroup', max_depth=0)
		checkbox = group.children.find(AXRole='AXCheckBox', max_depth=0)[2]
		if checkbox.AXValue == 0:
			checkbox.perform('AXPress')

		navigation = splitgroup.children.find_one(AXRole='AXSplitGroup', max_depth=0)
		recent_notes = navigation.children.find_one(AXRole='AXGroup', max_depth=0)
		recent_list = recent_notes.children.find_one(AXRole='AXTable', max_depth=1)
		recent_rows = list(recent_list.children.find(AXRole='AXRow', max_depth=0))
		current_row = recent_rows.index(next(row for row in recent_rows if row.AXSelected == True))
		desired_row = current_row + offset
		desired_row = max(desired_row, 0)
		desired_row = min(desired_row, len(recent_rows) - 1)
		recent_rows[desired_row].AXSelected = True
	
	def onenote_copy_link():
		onenote = onenote_app()
		# despite the name of this menu item, the link takes you directly to the selected paragraph
		(onenote.children.find_one(AXRole='AXMenuBar')
				.children.find_one(AXRole='AXMenuBarItem', AXTitle='Notebooks')
				.children[0].children.find_one(AXRole='AXMenuItem', AXTitle='Pages')
				.children[0].children.find_one(AXRole='AXMenuItem', AXTitle='Copy Link to Page')
		).perform('AXPress')
		app.notify(body='Copied link to paragraph', title='OneNote')

	def onenote_go_progress():
		window = onenote_window()

		# show navigation
		splitgroup = window.children.find_one(AXRole='AXSplitGroup', max_depth=0)
		group = splitgroup.children.find_one(AXRole='AXGroup', max_depth=0)
		checkbox = group.children.find_one(AXRole='AXCheckBox', max_depth=0)
		if checkbox.AXValue == 0:
			checkbox.perform('AXPress')

		# go to the first notebook
		navigation = splitgroup.children.find_one(AXRole='AXSplitGroup', max_depth=0)
		try:
			sections_pages = navigation.children.find_one(AXRole='AXSplitGroup', max_depth=0)
		except ui.UIErr:
			pass
		else:
			# sections and pages are visible; show notebooks instead
			notebooks_button = navigation.children.find_one(AXRole='AXButton', max_depth=0)
			notebooks_button.perform('AXPress')
		notebooks = navigation.children.find_one(AXRole='AXGroup', max_depth=0)
		notebooks_list = notebooks.children.find_one(AXRole='AXOutline')
		first_notebook = notebooks_list.children.find_one(AXRole='AXRow')
		if not first_notebook.AXSelected:
			first_notebook.AXSelected = True
			actions.key("return") # XXX auto-dismissal doesn't work when selected via accessibility
		else:
			notebooks_button = navigation.children.find_one(AXRole='AXButton', max_depth=0)
			notebooks_button.perform('AXPress')

		# wait for section and page navigation to reappear
		for attempt in range(5):
			try:
				sections_pages = navigation.children.find_one(AXRole='AXSplitGroup', max_depth=0)
			except ui.UIErr:
				actions.sleep("100ms")

		# go to the first section
		sections, pages = [child for child in sections_pages.children if child.AXRole == 'AXGroup']
		sections_list = sections.children.find_one(AXRole='AXOutline')
		first_section = sections_list.children.find_one(AXRole='AXRow')
		if not first_section.AXSelected:
			first_section.AXSelected = True

	def onenote_now():
		actions.key("ctrl-e enter")
		actions.key("cmd-alt-0") # custom shortcut for "Remove Tag"
		actions.key("cmd-/ cmd-.")
		actions.key("shift-tab:5 tab:2")
		actions.user.insert_time_ampm()
		actions.insert(" - ")
