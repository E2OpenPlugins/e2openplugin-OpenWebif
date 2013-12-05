# -*- coding: utf-8 -*-

# Language extension for distutils Python scripts. Based on this concept:
# http://wiki.maemo.org/Internationalize_a_Python_application
from distutils import cmd
from distutils.command.build import build as _build
import glob
import os

class build_trans(cmd.Command):
	description = 'Compile .po files into .mo files'
	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		s = os.path.join('locale')
		lang_domains = glob.glob(os.path.join(s, '*.pot'))
		if len(lang_domains):
			for lang in os.listdir(s):
				if lang.endswith('.po'):
					src = os.path.join(s, lang)
					lang = lang[:-3]
					destdir = os.path.join('plugin', 'locale', lang, 'LC_MESSAGES')
					if not os.path.exists(destdir):
						os.makedirs(destdir)
					for lang_domain in lang_domains:
						lang_domain = lang_domain.rsplit('/', 1)[1]
						dest = os.path.join(destdir, lang_domain[:-3] + 'mo')
						print "Language compile %s -> %s" % (src, dest)
						if os.system("msgfmt '%s' -o '%s'" % (src, dest)) != 0:
							raise Exception, "Failed to compile: " + src
		else:
			print "we got no domain -> no translation was compiled"

class build(_build):
	sub_commands = _build.sub_commands + [('build_trans', None)]
	def run(self):
		_build.run(self)

cmdclass = {
	'build': build,
	'build_trans': build_trans,
}
