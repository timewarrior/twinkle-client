repeat until application "Spotify" is running
	activate application "Spotify"
	delay 1
end repeat
activate application "Spotify"
tell application "System Events"
	keystroke "l" using command down
	keystroke "spotify:app:twinkle"
	delay 1
	keystroke return
end tell
