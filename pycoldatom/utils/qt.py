def qtstr(qtobj):
	return str(qtobj).replace('PyQt5.', '')

stateFunc = {
	'SpinBox': ('value', 'setValue'),
	'CheckBox': ('isChecked', 'setChecked'),
	'ComboBox': ('currentText', 'setCurrentText'),
	'Slider': ('value', 'setValue')
}