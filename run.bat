if "%1"=="hide" goto CmdBegin
start mshta vbscript:createobject("wscript.shell").run("""%~0"" hide",0)(window.close)&&exit
:CmdBegin
rem"D:\Users\user1\anaconda3\Scripts\activate.bat" anaconda的安装目录下的脚本
call D:\Users\user1\anaconda3\Scripts\activate.bat
:: daily_report为环境的名字
call activate daily_report
::代码所在的盘符
E:
::代码所在的路径
cd E:\code\daily_report
call python test_dmu.py