from talon import Module, Context

ctx = Context()
mod = Module()

ctx.matches = r"""
os: mac
and app.bundle: com.c-command.EagleFiler
"""

@ctx.action_class("user")
class eaglefiler_actions:
	def eaglefiler_select_first_displayed_record():
		from talon.mac import applescript
		applescript.run(f'tell application id "com.c-command.EagleFiler" to tell browser window 1 to set selected records to item 1 of (get displayed records)')

@mod.action_class
class EagleFilerActions:
	def eaglefiler_select_first_displayed_record():
		"""Select the first displayed record in the front message viewer in EagleFiler."""
