from talon import Context, Module, actions, imgui, settings, ui
import os

ctx = Context()
ctx.matches = r"""
app: apple_terminal
"""
directories_to_remap = {}
directories_to_exclude = {}

@ctx.action_class('app')
class AppActions:
	def tab_open():
		actions.key('cmd-t')
	def tab_close():
		actions.key('cmd-w')
	def tab_next():
		actions.key('ctrl-tab')
	def tab_previous():
		actions.key('ctrl-shift-tab')
	def window_open():
		actions.key('cmd-n')

@ctx.action_class('edit')
class EditActions:
	def paste():       actions.key('shift-insert')
	def copy():        actions.key('ctrl-insert')
	
	def delete():
		actions.key('ctrl-w')
	def extend_word_left():
		actions.key('ctrl-space')
		actions.key('alt-b')
	def extend_word_right():
		actions.key('ctrl-space')
		actions.key('alt-f')
	def delete_line():
		actions.key('ctrl-u')
	def word_left():
		actions.key('alt-b')
	def word_right():
		actions.key('alt-f')
	def line_start():
		actions.key('ctrl-a')
	def line_end():
		actions.key('ctrl-e')
	def page_down():
		actions.key('command-pagedown')
	def page_up():
		actions.key('command-pageup')
	def undo():
		actions.key('ctrl-_')

@ctx.action_class('user')
class UserActions:
	def file_manager_current_path():
		title = ui.active_window().title

		if "~" in title:
			title = os.path.expanduser(title)

		if title in directories_to_remap:
			title = directories_to_remap[title]

		if title in directories_to_exclude:
			title = None

		return title

	def file_manager_show_properties():
		"""Shows the properties for the file"""

	def file_manager_open_directory(path: str):
		"""opens the directory that's already visible in the view"""
		actions.insert("cd ")
		path = '"{}"'.format(path)
		actions.insert(path)
		actions.key("enter")
		actions.user.file_manager_refresh_title()
		
	def file_manager_open_parent():
		actions.insert('cd ..')
		actions.key('enter')
		
	def file_manager_select_directory(path: str):
		"""selects the directory"""
		actions.insert(path)

	def file_manager_new_folder(name: str):
		"""Creates a new folder in a gui filemanager or inserts the command to do so for terminals"""
		name = '"{}"'.format(name)

		actions.insert("mkdir " + name)

	def file_manager_open_file(path: str):
		"""opens the file"""
		actions.insert(path)
		actions.key("enter")

	def file_manager_select_file(path: str):
		"""selects the file"""
		actions.insert(path)

	def terminal_list_directories():
		actions.insert("ls")
		actions.key("enter")

	def terminal_list_all_directories():
		actions.insert("ls -a")
		actions.key("enter")

	def terminal_change_directory(path: str):
		actions.insert("cd {}".format(path))
		if path:
			actions.key("enter")

	def terminal_change_directory_root():
		"""Root of current drive"""
		actions.insert("cd /")
		actions.key("enter")

	def terminal_clear_screen():
		"""Clear screen"""
		actions.key("ctrl-l")

	def terminal_run_last():
		actions.key("up enter")

	def terminal_kill_all():
		actions.key("ctrl-c")
		actions.insert("y")
		actions.key("enter")

	def tab_overview():
		actions.key('cmd-shift-\\')
