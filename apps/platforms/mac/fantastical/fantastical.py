from talon import Module, Context

ctx = Context()
mod = Module()

ctx.matches = r"""
os: mac
"""

@ctx.action_class("user")
class fantastical_actions:
	def fantastical_parse(text: str):
		from talon.mac import applescript
		text = text.replace('"', '\"')
		applescript.run(f'tell app id "com.flexibits.fantastical2.mac" to parse sentence "{text}"')

	def fantastical_show_mini_calendar():
		import webbrowser
		webbrowser.open(f"x-fantastical3://show/mini")

	def fantastical_show_calendar():
		import webbrowser
		webbrowser.open(f"x-fantastical3://show/calendar")

@mod.action_class
class FantasticalActions:
	def fantastical_parse(text: str): """Parses the text in Fantastical."""
	def fantastical_show_mini_calendar(): """Shows the mini calendar popover."""
	def fantastical_show_calendar(): """Shows the calendar window."""
