Output docs/demo.gif

Require rrdoctor

Set Shell "cmd"
Set FontSize 18
Set Width 1180
Set Height 760
Set Padding 18
Set Framerate 12
Set TypingSpeed 18ms
Set Theme "Dracula"

Type "rrdoctor scan examples/unseeded-ml-repo --include RRD052,RRD091,RRD070 --fail-on none"
Enter
Sleep 2s
ScrollUp 28
Sleep 2s
ScrollDown 28
Sleep 1s
