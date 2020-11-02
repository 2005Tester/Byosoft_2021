chcp 437
del last_exception.log*
set cscript_path=C:\Cscripts
set tool_path=%~dp0

dflaunch %cscript_path%\startCscripts.py -a ipc -p CPX -s %tool_path%ErrorInjector.py %tool_path%TestLoader.py