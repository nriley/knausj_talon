from talon import actions, Module
from .user_settings import SETTINGS_DIR

mod = Module()

@mod.action_class
class Actions:
	def subl_talon_user():
		"""Edit Talon user (project if present, otherwise folder) with Sublime Text."""
		talon_project = list(actions.path.talon_home().glob('*.sublime-project'))
		if len(talon_project) == 1:
			actions.user.subl(talon_project)
			return
		actions.user.subl([actions.path.talon_user()])

	def subl_talon_user_settings():
		"""Edit Talon user settings with Sublime Text."""
		actions.user.subl(list(SETTINGS_DIR.glob('*.csv')))

