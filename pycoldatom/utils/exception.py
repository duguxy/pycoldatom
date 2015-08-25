class Suppressor:
	def __init__(self, exception_type, globalscope=None, localscope=None):
		self._exception_type = exception_type
		self._gs = globalscope
		self._ls = localscope

	def __call__(self, expression):
		try:
			exec(expression, self._gs, self._ls)
		except self._exception_type as e:
			print('Suppressor: suppressed exception %s with content "%s"' % (type(e), e))
			# or log.msg('...')