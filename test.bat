
@echo off
REM Looping test runner for main.py — iterates over (r,c) and query types and appends parameters + output to a single file
set OUTPUT=test_output.txt

echo Test run started at %DATE% %TIME% > %OUTPUT%
echo ======================================= >> %OUTPUT%

REM Activate conda environment (works with "conda activate" available in PATH)
call conda activate diplomatico

REM Define board sizes (r,c) pairs and query types
setlocal enabledelayedexpansion
set SIZES="4,5" "4,6" "4,7" "5,5"
set QTYPES=CONSTRUCTIVE APOC PYTHON

echo Phase A: runs with --n 1 >> %OUTPUT%
for %%S in (%SIZES%) do (
	for %%Q in (%QTYPES%) do (
		for /f "tokens=1,2 delims=," %%A in ("%%~S") do (
			set R=%%A
			set C=%%B
			set /a END_COL=!C!-2
			echo Parameters: --r !R! --c !C! --query_type %%Q --n 1 --starting_node 2,0 --ending_node 3,!END_COL! --t 10 >> %OUTPUT%
			python main.py --r !R! --c !C! --query_type %%Q --n 1 --starting_node 2,0 --ending_node 3,!END_COL! --t 10 >> %OUTPUT% 2>&1
			echo. >> %OUTPUT%
		)
	)
)

echo Phase B: runs without --n (use default behavior) >> %OUTPUT%
for %%S in (%SIZES%) do (
	for %%Q in (%QTYPES%) do (
		for /f "tokens=1,2 delims=," %%A in ("%%~S") do (
			set R=%%A
			set C=%%B
			set /a END_COL=!C!-2
			echo Parameters: --r !R! --c !C! --query_type %%Q --starting_node 2,0 --ending_node 3,!END_COL! --t 10 >> %OUTPUT%
			python main.py --r !R! --c !C! --query_type %%Q --starting_node 2,0 --ending_node 3,!END_COL! --t 10 >> %OUTPUT% 2>&1
			echo. >> %OUTPUT%
		)
	)
)

echo Test run finished at %DATE% %TIME% >> %OUTPUT%
echo ======================================= >> %OUTPUT%
echo Results saved to %OUTPUT%
