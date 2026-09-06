# Changelog

All notable changes to Realistic Walking Camera.
Format is roughly Keep a Changelog. Dates are YYYY-MM-DD.

## [Unreleased]

### The Director gets its own tab, and Play actually moves the camera (2026-09-05)

The replay keyframes were half a feature living inside the Recorder tab. You
could add markers and nothing else: no save, no way back to a marker, no way to
delete one, and Play moved nothing. Rebuilt around how the Rockstar Editor
works, and kept to that: markers on the clip, skip between them, edit the camera
at one, save the project. No per-marker speed, no filters, no effects.

**Play did nothing, and this is why.** The only code that reads the marker list
sits behind `not walkingActive`, and walkingActive is true exactly when you are
ON FOOT watching a replay, which is the whole use case. The list filled up and
its only reader never ran. While the director is playing it now owns the camera,
which is what a preview does. It needs two markers: with one there is no move to
play, and stealing the camera to hold a single pose would be worse than nothing.

**The bar has a mouse now.** There was not one mouse read in timeline.lua: the
ticks were `drawLine` and nothing else. Click a marker to select it, drag it to
move it in time, click anywhere else to seek. Two markers cannot land on the same
frame, because a zero-length span is the teleport the interpolator already has
code to avoid.

**Go to it, Re-aim here, Delete.** Re-aim is the editor's "edit camera": keep the
marker where it is in time and replace its camera with the one you are looking
through. Before this, a badly framed marker could only be deleted with Undo, and
only if it was the last one.

**Prev and Next.** The two skip buttons from the Rockstar panel. Without them
there was no way back to a marker except hunting for the frame by hand on the
scrub bar.

**Save and load.** A shot list is a text file in `director/`, one marker per
line, eight numbers: frame, position, look, fov. Not JSON on purpose. The shape
is flat and fixed, so a parser would be more code and more ways to fail than a
format you can open in Notepad when someone says their take vanished.

The Recorder tab keeps everything it had. The two were different things sharing
one tab, which is what made it confusing.

### The recorder: the zoom that breathed, and a K that deleted (2026-09-05)

Three reports, and the audit that chased them found the causes in different
places from where they looked.

**The zoom drifting while a take plays back.** The playback writes the recorded
FOV every frame, and the DISCRETE zoom easer kept running afterwards in the same
pass of updateWalkingMode and pulled it back. Because the target is rewritten
every frame the easer never converges: it just applies a fixed fraction of the
gap per frame, and that fraction is a function of dt. Measured from the
constants: 2.9 percent of the gap at 60 fps, 10.5 percent at 30. The same take
renders at a different zoom depending on frame time, which is what looks like
the image breathing. The playback block now clears discreteZoomMode and
zoomVelocity, the same pair the FOV slider and the focal presets already write.
Nothing decides differently; the easer just stops fighting over a value the
playback owns.

**The phone was still writing FOV during playback.** It was the only one of the
three phone channels without a playback guard: look direction and roll both had
one. Touching the zoom in the app during a take moved the take.

**Shift+K deletes, and SHIFT is Run.** Walking fast holds SHIFT, and SHIFT is
also the dolly's "remove last keyframe" modifier. Press K while running and the
mod removes instead of adding, and the only trace of it was behind RWC_DEBUG,
which is false by default. The list shrinks in silence, which reads exactly as
"the add-keyframe button does not work". The removal now says so on screen. The
binding is not changed: that is the owner's to decide.

**The timeline's Add keyframe was a silent no-op outside a replay.**
Timeline.addKeyframe returns false when no replay is running and the return was
discarded with no message. The K path has always announced itself; this was the
only mute one.

**The replay bar is not missing, it is in the other tab.** It draws in
Features > Recorder, only during an active AC replay, and its ticks come from
the timeline's own keyframe list, which is NOT the list the K key fills. Those
two lists have incompatible axes: a timeline keyframe carries a replay frame
number, a dolly keyframe carries no time at all. A line in the Dolly tab now
says where the bar is and that the two lists are separate. Making the bar
control keyframes is new code, not a fix: there is no hit-test in timeline.lua
at all, only drawing.

### The viewfinder shows the game, or nothing (2026-09-05)

The desktop was reaching people's phones, and the route was the fallback.

video.ini on this machine has FULLSCREEN=1. Windows.Graphics.Capture cannot
capture true exclusive fullscreen, so `gfxcapture=window_exe=acs.exe` returned
no frames, three attempts failed, and the server demoted itself to Desktop
Duplication, which copies the whole monitor. Minimising the game produces the
same no-frame symptom and nobody was checking for it, so alt-tabbing once was
enough to put the desktop on the phone for the rest of the session: the demotion
wrote `state["backend"] = "dda"` and nothing ever wrote it back.

Four changes, and they are all about not showing the wrong thing:

The server now asks about the game's WINDOW and not only its process. Absent,
minimised, behind another window, visible, and whether it covers the screen.
`game_running()` only ever answered "the process exists", which stays true
through all of those.

It holds the picture instead of sending something else. Minimised, or behind
another window while on the whole-screen capture, and the phone gets nothing and
a line saying why. Black beats somebody's desktop.

The demotion is gated on the window covering the screen. That is what exclusive
fullscreen looks like, and there Desktop Duplication IS the game. When the
window does not cover the screen there is no case in which the desktop is the
better answer.

The demotion is no longer for the session. A good attach with a window that does
not cover the screen returns to window capture.

And the mod reads `viewfinder-error.txt`, which the server has been writing since
the beginning with NO reader anywhere. Every explanation it produced went to disk
and the tab showed an absence of picture. Exclusive fullscreen now says so, with
the fix, in the Phone Gyro tab.

⚠️ The .exe was rebuilt. Editing viewfinder-udp.py alone ships nothing, which
build-viewfinder.py warns about in its own header. Both app folders carry the
same binary now: they had drifted by 40 KB of source, and the mod resolves the
Mobile Cam folder first.

### One viewfinder server for both mods (2026-09-04)

Both this mod and Mobile Cam ship the same viewfinder server and both bind UDP
9877. Only one process can hold that port, so the second one exits - and because
every path each app uses (the mode file, the status file, the command file, the
peer file) is derived from the folder that app resolved for ITSELF, and each one
looked in its own folder first, the loser spent the session writing mode changes
into a file the winner never reads. Its buttons did nothing, and every mode
looked the same because the mode never changed.

That was the live state of this machine tonight: this mod's copy held 9877 and
streamed a session, while Mobile Cam's log filled with "UDP 9877 is taken by
another copy. exiting." every ten seconds as its watchdog relaunched a copy that
could never win.

Restart also writes its "quit" into both folders now, not just the resolved one.
A server left running from the other folder holds UDP 9877 and reads only its own
command file, so Restart would ask a process that is not running to stop and then
relaunch a copy that loses the port again - a dead button in front of a picture
that never changes, and exactly what the first launch after this change would hit
with an older server still alive from the previous session.

The candidate list here now resolves to the same folder Mobile Cam resolves to,
so there is one server, one mode file and one status file. Whichever app is on
screen, its buttons reach the process that is actually running, and neither app
relaunches a copy that cannot take the port. A machine with only one of the two
mods installed is unaffected: the list falls through to whichever folder exists.
Nothing else in this mod changed.

### The phone aim no longer snaps at the ends of the yaw (2026-09-03)

Turn the phone until the aim sits near half a turn from where it was
calibrated and keep going: the camera used to snap the other way. The yaw the
receiver works with lives on the [-180, 180] chart (the phone's own, and the
interpolation step on this side re-creates it), and that chart was multiplied
by Sensitivity and pushed through the One Euro filter as if it were a plain
number. Neither stage is wrap-aware. At sensitivity 1.2, +179
becomes +214.8 and -179 becomes -214.8, which are 70 degrees apart as
directions, and the filter then slews the long way round through zero. That
slew is the jump.

The receiver now accumulates the wrapped delta of every sample into a
continuous angle, yaw and roll (pitch is gimbal-limited and never crosses),
BEFORE the sensitivity multiply and the filter, so both only ever see a smooth
signal. The mod adds it to finalYaw, which is unbounded by design, so a value
past 180 is just another direction. The accumulator arms on the first sample
and re-arms on connect and on Calibrate, because the phone restarts its chart
at zero there and the first packet after it would otherwise read as one giant
delta. It logs once when it arms, never per packet. A phone that already
streams an unbounded angle (the Android app has integrated its own deltas
since the gimbal wrap entry further down this file) passes through unchanged:
the delta of a continuous signal is the signal.

One consumer needed a matching touch: the avatar head-bone tracking clamps the
smoothed yaw to +-60 degrees, and a continuous angle would have left the head
pinned at the clamp after one full physical lap. It now wraps the angle back
onto (-180, 180] before clamping, which is exactly what it saw before.

This is the Mobile Cam's fix, ported because both apps ship the same receiver
module. Checked offline with a harness that runs the real block out of this
file: forward and backward crossings stay continuous, a crossing scaled by 1.2
stays smooth, two full laps accumulate to exactly 530, roll unwraps too, an
already-continuous stream (steps under 180 degrees, up to 150 in the test)
comes back unchanged, and a reset followed by a first packet does not jump. The
touched file compiles under Lua 5.4.

### Open OBS no longer kills the viewfinder: automatic MJPEG fallback (2026-09-02)

This GPU (RTX 3070 Ti / GA104) has ONE physical NVENC engine, and there is no
iGPU on the 5800X. So an H.264/HEVC viewfinder mode and OBS both want the single
NVENC engine, and under that load the viewfinder's encode starves - the measured
"open OBS and it becomes unusable". MJPEG encodes on the CPU and touches no NVENC.

The server now detects OBS (obs64/obs32/obs.exe, via the same Toolhelp scan as the
game check, cached ~2 s) and, while OBS is open, serves MJPEG (hq) in place of any
NVENC mode - so the two never fight for the engine. When OBS closes, the next
stream returns to the mode actually requested. Verified: detection flips True with
a live obs*.exe and False without. viewfinder-udp.exe rebuilt.

### The encoder could stall at zero frames forever; now it self-restarts (2026-09-02)

Watched live with the game open: the viewfinder auto-started the instant AC
launched, WGC (gfxcapture) latched onto the window while it was still on the
loading screen, and the encoder then sat at ZERO frames for four and a half
minutes - only a manual mode change freed it. A fresh capture of the very same
window works, so the attach lost a startup race; the encoder is not wrong.

Why it could never recover on its own: when WGC delivers nothing, ffmpeg emits
nothing, so `p.stdout.read()` blocks with no data. The stream loop never turns,
so the mode/game checks never run AND the existing "WGC produced no frames -> fall
back" path at the end is never reached. It was a silent, permanent freeze.

Fix: a watchdog thread kills a silent ffmpeg after 6 s with no first frame, which
unblocks the read and lets the loop exit into a retry. And because a fresh WGC
attach works, the no-frame path now retries WGC up to 3 times before demoting to
Desktop Duplication, instead of giving up the better capture on the first stall.
Verified the watchdog does not touch a healthy stream (loopback still streams
clean, no false kill). This is the missing half of "nothing shows when I open AC":
the auto-start races the load and used to lose for the whole session.

### THE bug behind "Sharp is horrible": MJPEG portrait encoded nothing (2026-09-02)

Caught live, with the game running and the phone streaming. In `hd` (H.264) the
server sent a steady 30 fps and the phone reported `fps=35 lost=0` - smooth, zero
loss, on the same LAN. The moment the phone switched to `hq` ("Sharp", an MJPEG
mode) the server's frame counter went to 0 and stayed there, and the server log
(now kept, see below) said why:

    Error configuring filter graph: Function not implemented (-40)
    Could not open encoder before EOF ... Invalid argument (-22)

Cause: in PORTRAIT the capture does its crop in software, so the grab filter
already ends past a `hwdownload,format=bgra`. `ffmpeg_cmd` then appended a SECOND
`hwdownload` for every MJPEG mode, asking the graph to download frames that are no
longer on the GPU - which ffmpeg refuses, so the MJPEG encoder never opens and not
one frame is produced. Every MJPEG mode (mjpeg, hq, low) was dead in portrait, and
portrait is what the phone uses. H.264 was unaffected (it skips that append), which
is why `hd`/`max` worked while the "lighter" modes looked broken - the exact
opposite of the intuition that lighter = safer.

Fix: only append the readback when the grab has not already done one
(`"hwdownload" not in grab`). Verified: mjpeg/hq/low portrait now encode at 57/57/29
fps (screen capture, game closed) where they produced 0 before; hd unchanged.
viewfinder-udp.exe rebuilt.

### The "4 fps on every mode" red herring: the server was also crashing on its own print (2026-09-02)

The keyframe story below is real but was NOT the whole answer: the owner reported
that EVERY mode stutters, MJPEG included, which the keyframe explanation cannot
account for (MJPEG has no keyframe to lose). Measured on his machine instead of
theorised:

- Capture + encode: 57 fps on every mode (mjpeg/hd/max, WGC and DDA). Fine.
- The whole send path (pacer, fragmentation) over loopback: 57 fps, zero loss,
  smooth. Fine. So the PC produces AND sends frames correctly on all modes.

The bug is that the server was DYING. It is built --noconsole, and the mod launches
it with no console and no reader on its output. On Windows that leaves stdout/stderr
invalid, and `print(..., flush=True)` against an invalid handle raises
`OSError [Errno 22]`. The server prints constantly while streaming, so any one of
those could take the whole process down mid-stream - and it did, caught twice in
viewfinder-crash.log, both at a `print()` inside `stream()`. When it dies the video
stops on every mode until the mod's watchdog relaunches it, which on the phone is a
few-fps, "losing connection" stutter. It never appeared in any test run from a
terminal, because a terminal gives print() a real handle - which is why every
measurement so far missed it.

Fix: when frozen, the server points its own output at `viewfinder-log.txt` next to
the exe, so no print can raise; and the main loop now wraps `stream()` so a single
bad stream is logged and retried instead of exiting the process. Two wins: the
crash class is gone, and for the first time the server's live narration is kept on
disk instead of thrown at a dead handle. viewfinder-udp.exe rebuilt and verified
(the frozen exe now writes the log and stays up).

### The keyframe is now armoured, so "4 fps only on max" is fixed (2026-09-02)

The owner's viewfinder ran at ~4 fps on the `max` mode while every other tester
was smooth, on strong Wi-Fi right next to the AP. Measured across the whole
pipeline, the cause is not bandwidth and not the link:

- On `max` (H.264, portrait ~666x1440, one IDR keyframe per second) each frame is
  cut into UDP fragments. The keyframe is the biggest NAL: 60-285 fragments.
- The per-frame XOR parity rebuilds exactly ONE lost fragment. So the moment a
  frame loses two, it is gone - and for an H.264/HEVC stream the phone then drops
  every following frame until a WHOLE keyframe survives (a P-frame predicted from a
  lost reference would smear). The server cannot force a keyframe on demand, so the
  wait runs to the next natural one, up to a second away.
- A big keyframe, protected by a single-loss parity, rarely survives on any
  imperfect link. So the picture spends most of every second waiting = a few fps.
  MJPEG and the lighter modes are immune (every frame independent, small, no
  keyframe to wait for), which is why other testers never saw it.

Fix, server-side only, no protocol change, works with every phone already
installed: the keyframe's data fragments are now sent THREE times, and the copies
are spread a whole frame apart so one burst cannot eat all three. Per-datagram loss
the keyframe must beat drops from p to p-cubed: a 2% link goes from ~35% keyframe
survival to over 99%. Parameter sets (SPS/PPS/VPS) go out twice for the same
reason. Ordinary P-slices stay single, protected by the existing parity. The phone
dedupes copies by fragment index, so an updated app is not required and nothing on
the wire changed. viewfinder-udp.exe rebuilt.

### The Pure PP look, done the Mobile Cam way, v2.2.0 (2026-08-31, late night)

The mod now wears Pure PP's organisation the SAME way the Mobile Cam does,
which is the version signed off on: stock Assetto Corsa styling everywhere,
with only Pure's tab row and dark fields borrowed. The pureTabRow function is
ported across verbatim, so the two mods match.

- Category row is Pure's tab row: text-width buttons, the active one filled
  RED (not the earlier green), a 2px colour identity bar under each category,
  a thin line under the row.
- Pure's translucent-black field background over the panel.
- Sliders match the Mobile Cam: stock 200px, and the value text warms to
  YELLOW while it is off its default (Pure's "this was touched" cue).
- Version in the header is a constant now (was hardcoded v2.1.0), and the
  Preset line turns yellow with a * when there are unsaved changes.
- PRESETS ARE .LUA SCRIPTS (modulos/preset_scripts.lua): sorted keys,
  hand-editable, an optional apply(cfg) that can compute, run sandboxed
  (math/string/table only). Old .ini presets still load and gain a .lua twin
  automatically. The Export/Import dialog is replaced by a one-line strip.
- Pure's bottom row: SAVE / LOAD / DEFAULTS / DELETE on the active preset,
  SAVE amber while dirty, LOAD/DELETE hidden with no file, DELETE asks twice.

An earlier attempt wrapped the window in a UI library that repainted fonts
and colours wholesale; that was wrong and is reverted. No UI library touches
the mod's appearance now.
### The 180 Hz capture fix, honest tabs, and total silence (2026-08-31, night)

THE owner's-PC-only viewfinder collapse, finally measured: gfxcapture's
max_framerate does not cap on his 180 Hz monitor. Asked for 30 fps it
delivered 178 (1074 frames in a 6 s bench, reproduced), so NVENC, the
splitter, the pacer, the Wi-Fi and the phone's decoder all ate SIX TIMES
their designed load - the "1 fps, travado, so no meu PC" report in one
number. An explicit fps filter after the capture drops the excess before the
encoder sees it; the same bench comes out at exactly 30. Everyone else runs
60 Hz monitors, which is why only he collapsed while testers only saw delay.

Tabs: one selected top tab at a time (Performance Cost pushed a bright blue
unconditionally and always read as active), and the sub-tab bar id now
carries the category - a fixed id meant imgui kept a selection by hash for a
child set that changed per category, falling back to the first submitted tab
(an ungated Homespace Cam) whenever the remembered one vanished. Homespace
Cam is gated under Camera, Phone Gyro under Features, Motion (FPS) moved to
Debug where its own closing comment said it belonged, and the Phone Gyro
diagnostics moved wholesale to Debug > Phone Diag. The obsolete 7-step
Android how-to died; quality buttons are full-width with labels that fit and
say what to pick; transports are named for when to use them.

Silence: os.execute and io.popen('dir') spawn VISIBLE cmd windows, and they
fired at app load (mkdir on fresh installs), on preset scans, on template
scans, on BVH scans and on the Open Presets Folder button. All replaced with
CSP's windowless io.createDir / io.scanDir / explorer via runConsoleProcess,
in both mods. The viewfinder exe is built --noconsole now, with its ffmpeg
child already CREATE_NO_WINDOW plus above-normal priority, and the 15-minute
render-sync scheduled task got a wscript wrapper so its blue PowerShell
flash mid-race is gone.

One-shots: the capture source lifts back to Game window (the desktop source
is what made the picture read as "2D"), keeping any later manual choice.

### Connection without typing, USB that tells the truth, keys that respect the keyboard (2026-08-31)

Enabling Phone Gyro now switches third-person OFF (same cleanup the car-entry
path does): the phone drives a first-person body, and both at once fought
over the camera.

Every bind that polled keys directly is now quiet while a UI text field owns
the keyboard. Typing an IP used to walk the camera (WASD), enter the car (E),
jump (Space), flip the knife (F) and toggle the flashlight (Q). The central
isKeyOrPadDown was already guarded; input, movement, carcontrol, flashlight,
knife, forzavista, camera_effects and eight direct sites in the main file now
share the same wantCaptureKeyboard gate.

USB was Android-only (adb) and, worse, poisoned the video server: the
adb-forward address 127.0.0.1 went into the peer file and the server streamed
every frame to its own loopback while the status said connected. Guarded on
both sides now. The iPhone path is Personal Hotspot over the cable: a real IP
subnet (PC 172.20.10.x, phone .1) where the control socket and the UDP video
both flow - the server probes it and the phone appears in the discovery list
as a `usb` row, the fastest link there is. adb stays as the Android path,
labelled honestly: control only.

The discovery list dedupes: hello v2 (app build 92+) carries the phone's own
tailnet address, so at home one handset is ONE button - the Wi-Fi one -
instead of a wifi row and a tailscale row for the same phone.

Server: NVENC is probed once at startup and an encoder death is attributed
to the right half of the pipeline - a machine without NVENC falls back to
MJPEG HQ for the session instead of respawning a dead encoder twice a second
with the error thrown away (stderr now lands in the log). Two stale
mode=="h264" checks gave hd/max/hevc the MJPEG pacer estimate; fixed. With
that net in place the default mode becomes `max` (one-shot lift for installs
that persisted the old mjpeg default).

### The 6DOF distance box is gone from every place it lived (2026-08-31)

The earlier removal raised the fallback table in sixdof.lua to a kilometre
and stopped there, and that fallback is only read when the config carries no
value, which it always does. So the box a tester walked into ("its like a box
i guess", stopping dead trying to walk behind the car) stayed live in every
build ever shipped. A 31-agent sweep of the whole path (app, wire, both mods,
distribution) found five sources of the number; four are fixed here and one
was already dead code:

- config.lua defaults: 3.00/2.00/3.00 m are now 1000.0 on all three axes.
- settings.lua declares the same numbers twice (ac.storage schema and
  defaultValues); both lifted.
- Persisted state: every existing install saved the old walls into its own
  state ini, so a one-shot migration (sixdofLimitLift stamp) lifts any stored
  translation limit at or under the old 12 m slider cap to 1000 on next load.
- The Move less, see more ratio buttons wrote a "reach" wall with every press
  (1:1 restored the exact 3 m box, vertical 1.2 m) and saved it. They now set
  scale and smoothing only.
- SixDof.applyRig still writes per-rig limits but has zero call sites since
  the rig buttons were removed; left as a programmatic API.

The kilometre is kept instead of no clamp at all: it is unreachable on foot
and still catches an ARKit pose that has gone to nonsense. The per-axis Clamp
slider remains for anyone who wants a wall on purpose.

### HEVC viewfinder mode (2026-08-31)

New "HEVC 1920x1080 60fps" button on the Screen on phone list, in both mods.
The server encodes with hevc_nvenc instead of h264_nvenc; everything else in
the pipeline (Annex-B splitter, pacer, XOR parity, the mode file) is the same
machinery. On the wire it is flags bit 1 on every datagram, with the kind byte
carrying the HEVC NAL type; the disambiguation exists because HEVC's TRAIL_N
is type 0, which is the JPEG kind.

Why: the same picture costs roughly two thirds of the bits, which is fewer UDP
fragments per frame, and a frame dies if any one fragment dies. On 5G through
the Tailscale tunnel or on crowded Wi-Fi the shorter frame survives where the
H.264 one does not. Needs app build 91 or later on the phone; an older app
draws nothing on this mode (it reads the frame as JPEG and quietly fails), so
if a tester picks it and sees black, the app is old.

Wire test: 4,403 NALs streamed, kinds 32/33/34 (VPS/SPS/PPS), 19 (IDR) and
1/39 as expected, every datagram flagged.

### The phone's CAR button is an aim assist now, not a takeover (2026-08-27)

Holding CAR used to switch `TrackingModule` on, which hands the camera over
wholesale. That is the opposite of what the button is for: you want to run, and
you want the car to stay in frame, and you want to keep deciding what the shot
looks like the entire time.

CAR now drives `modulos/car_assist.lua`, which decides nothing. It adds a slow
corrective turn to your BODY heading — `state.yaw` / `state.pitch` — and stops
there. The phone's orientation is applied on top of those a few lines later, so
the assist is structurally incapable of fighting the gyro: turn the phone and the
shot turns exactly as much as it always did. What moved is your shoulders.

Four things keep it from feeling like an aimbot:

- **A dead zone.** Inside 4 degrees of the target it contributes exactly zero —
  not a little, zero. Fine framing stays yours, and the camera never crawls in
  slow circles around a parked car.
- **A rate ceiling.** The correction is a turn RATE, not a position, so there is
  no mechanism by which it could snap. The worst it can do is turn at 8 deg/s
  for as long as the car is off frame.
- **Acceleration limiting.** The rate itself is lowpassed, so it leans into a
  turn and out of it the way a person does instead of stepping like a servo.
- **Yielding.** While you are actively swinging the phone it hands authority
  back — a correction layered on top of a deliberate pan is exactly what feels
  like fighting the controls. It returns as soon as you settle.

It stays out of the way of anything that owns the camera outright: the aimbot
while locked, tracking while enabled, and third person (where `finalYaw` is
discarded entirely, so the correction would be invisible while still silently
rotating your body under the shot).

Target priority on the press: whatever you picked in the phone's CARS list, then
whatever you are actually pointing at (one raycast), then the best thing in
frame. It releases when the car retires.

Measured, in `tests/test_car_assist.lua`, which runs without the game:

| situation | result |
|---|---|
| car parked 40 deg off axis | settles at 3.07 deg, peak 8.00 deg/s, jerk 13.6 deg/s2 |
| car crossing at 100 km/h, 45 m out | takes 48.8 deg of turning off you in 10 s |
| you swing the phone deliberately | authority drops to 0.15, back to 1.00 when you stop |
| target inside the dead zone | 0.000000 deg contributed |

Sliders live under AIM FRICTION in the Mouse/Aim tab, with a live readout of
error, authority and current turn rate. They persist on their own through
`Settings.saveGeneric` — no whitelist to maintain.

Note for anyone who had CAR mapped: the behaviour changed. It no longer engages
tracking. TRACK still does.


### The viewfinder was streaming to one phone at a time (2026-08-27)

The server kept a single client address and overwrote it on every hello, so two
connected devices took turns. The log showed the destination flipping eleven
times in twelve seconds — each device getting half the frames with a one-second
hole between them, which is indistinguishable from the capture stuttering and is
not the capture.

`send_frame` now fans each fragment out to every phone that has said hello in the
last five seconds. The pacer is charged once per fragment rather than once per
phone: it exists to stop one frame arriving as a single burst, and that shape is
the same however many addresses it goes to.

Measured on loopback with a second device connected and the game at 95% GPU:

| | before | after |
|---|---|---|
| frames delivered | 29.3/s | 59.9/s |
| p99 gap | 1246 ms | 33 ms |
| worst gap | 1277 ms | 54 ms |

This is very likely what "the viewfinder still stutters" has been for some time.
Any measurement taken with one client could not see it.


### A phone joining an H.264 stream mid-flight showed nothing (2026-08-27)

The stream uses intra-refresh — a moving band of intra blocks instead of periodic
keyframes — so there is no IDR to join on, and NVENC emits SPS/PPS exactly once
at the start. A phone that connected a second later never received the parameter
sets and could not decode a single frame. Verified: a cold join decodes 0 frames
and complains about a non-existent PPS.

The parameter sets are now cached and re-sent once a second, and immediately to
any address that has not had them yet. A second client measured 74 ms from hello
to SPS instead of up to a second.

The stream itself was never the problem. With the parameter sets in front of it,
the same capture decodes 779 frames with zero errors.

Also measured while proving this out, because it decides which mode to use when
things get heavy: under load the frame RATE never drops (58.9-60.1/s with four
extra full-resolution capture processes fighting for the GPU). What load costs is
the worst case — MJPEG's largest gap goes from 83 ms to 189 ms, while H.264's
stays pinned near 48 ms regardless. And MJPEG's bitrate follows scene detail
(12.4 Mbit on a simple scene, 38.7 on a busy one, ~67 UDP fragments per frame
where any single loss kills the whole frame) while H.264 sits at 1.0 Mbit and 2
fragments. MJPEG remains the default; H.264 is the answer for a weak Wi-Fi or a
heavy scene.


### The viewfinder server stops stat-ing its mode file 250 times a second (2026-08-27)

`stream()` checked `viewfinder-mode.txt` at the top of every loop turn, and the
loop turns once per 8 KB read - about five times a frame, ~250 `os.stat` calls a
second on a deep Program Files path, measured at 2-4% of a core spent asking
whether a human had pressed a button. It polls twice a second now.

Measured honestly: this buys NO smoothness. The reclaimed time goes straight back
into blocking on the pipe, which is where the loop was waiting anyway. It is a
cleanup, and it is in the changelog as one.

Nothing else about the server changed, deliberately. The viewfinder's judder was
traced to `ddagrab`'s own frame pacing - it stamps a frame when something
downstream asks for one rather than on a clock - and the two obvious answers both
fail on measurement: appending `fps=60` regularises timestamps that
`-f mjpeg pipe:1` discards a stage later (and doubled the over-33ms share), and
scaling on the GPU before the 14.7 MB/frame readback cannot be built in this
ffmpeg (`scale_d3d11` fails to create its texture, `hwmap` to CUDA and Vulkan are
not implemented). The fix that worked is on the phones: a presentation clock.


### The phone's AIM draws a crosshair again, and drops it when it locks (2026-08-27)

Both halves were wrong, in opposite directions.

State 1 - free aiming, the state whose whole job is letting you choose the point
- drew nothing. The crosshair renders on `AimbotModule.isAiming()`, which is set
by `startAiming()`, which is what the B key calls and what the phone's block
never did. It enabled the aimbot and turned natural tracking on, so the aim
worked; there was just no mark on screen telling you where it was pointing. You
were aiming blind.

State 2 - locked - kept drawing. The renderer's condition is
`isAiming() or isLocked() or crosshairVisible`, and locking sets the lock mode
without clearing the aiming flag, so after tapping through AIM to LOCKED both of
the first two were true. The crosshair exists to show you where you are pointing
WHILE you choose; once the point is chosen it is a mark sitting in the middle of
the shot.

`state.phoneAimLocked` now gates both renderers - `windowCrosshair` and the
second one inside `windowMain`. It is deliberately separate from
`crosshairVisible`, which belongs to the B key's own 1.5s auto-hide timer; the
two must not fight. And `startAiming()` goes after the unlock in the free-aiming
branch, because `unlock()` clears the very flag it sets.

`tests/test_aim_crosshair.lua` pins both halves: the module assumptions the fix
rests on, checked against the real `aimbot.lua`, and the wiring in the main file,
which cannot be run outside the game.


### The phone's REC saves the take by itself (2026-08-27)

`Recorder.stopAndSave()` and `Recorder.autoName()` are new, and the phone's REC
uses them. The keybind is deliberately untouched: whoever pressed it is at the
keyboard with the save dialog one key away, and it is also the re-record
workflow, so auto-saving every stop would litter `templates/` with every attempt.
From the phone there is no dialog to reach, so a take not saved on stop is a take
that is gone the next time you press record.

The name is `path_<YYYYMMDD>_<HHMMSS>_<track>_<car>`. The prefix and the
timestamp's position are not free choices - `scanTemplates` sorts alphabetically
and "play the most recent" reads the LAST entry, so anything else would break
that ordering against every take saved before it. Track and car come from
`ac.getTrackFullID` / `ac.getCarID`, both pcall'd and both optional: a name is
better with them and still works without, and a take is not worth losing to a
missing API on some CSP version. Everything is reduced to `[A-Za-z0-9_-]` and
capped, because these ids come from the sim and can contain spaces, slashes,
dots, accents, or two hundred characters against a path that is already a hundred
deep before the name starts.

The result is pushed back to the phone as `{"cmd":"recsaved",...}` - it is the
only feedback someone holding the phone can get.


### The phone can drive the take recorder, and AIM is three taps (2026-08-26)

- **REC on the phone is THIS recorder.** The app sends `rec` and it runs the same
  start/stop the RECORDER_TOGGLE keybind runs - not a copy of it. Duplicating the
  logic would mean two recorders drifting apart; this way the phone is another
  button on the one recorder, and the save dialog and template list are untouched.
  The mod pushes `recstate` back (on change, and twice a second while rolling, with
  the frame count and elapsed time), so the phone shows what is actually happening
  in the game rather than what it last asked for - including a take started or
  stopped on the PC.
- **AIM is three states instead of hold-to-lock.** Holding locked the point at the
  instant you pressed, which is never the point you wanted. Now state 1 turns the
  aimbot on with the crosshair following the phone so you can place it, state 2
  locks it there, state 0 restores whatever the aimbot was set to before. An older
  phone build that only sends the boolean still reads as hold-to-lock.
- **Held phone buttons are released when the phone goes away.** Track, Aim, Aim
  Car and the new three-state AIM all latch on a packet; the phone can vanish
  mid-hold - Wi-Fi drop, app killed, screen locked - and nothing ever told the
  mod it let go. With hold-to-lock that was already wrong; with a three-state AIM
  it is worse, because state 2 is a latch rather than a hold, so the aimbot stayed
  locked on with no button anywhere to release it. Every held button is now
  cleared on disconnect and on the stale-data reset.
- **A phone shortcut pressed while not walking is dropped, not queued.** The
  shortcut is queued from the socket callback and only consumed inside the phone
  block, which runs only while walking on foot. Press REC in the car and the
  command sat in the queue until you got out - then the take recorder started by
  itself, minutes later, for no visible reason.
- **Manual roll (Q/E and its pad bindings) is silenced while the phone is the
  camera.** `manualRollTarget` is an integrator, so an input stuck at 1 - a held
  key, a bound pad button, a drifting wheel axis - ramps the roll rather than
  nudging it, and because it only reached `finalRoll` inside the tracking block it
  showed up as "the camera starts spinning the moment I press Track or Aim Car"
  while looking fine the rest of the time. With the phone connected the physical
  tilt of the phone IS the roll, 1:1; a second source fighting it is not a feature.
  Q/E is unchanged without the phone.

### Double-check on the reported case: landscape -> portrait (2026-08-26)
Two more things were still standing between "the axes are decoupled" and "the
camera IS the phone". Both were found by closing the loop end to end: running the
numbers the app sends through the mod's own `lookDir`/`up` formula and comparing
the resulting camera basis against where the phone is really pointing, at every
step of a move rather than only at the end (`tests/end_to_end_1to1.py` in the iOS
repo).

- **The phone's roll was inside the "Apply Roll Effect" block.** That checkbox
  belongs to the X-button roll and the walking sway - things that genuinely are
  effects. The phone's roll is not an effect, it is how the operator is physically
  holding the camera, so unticking that box silently threw the camera's real
  orientation away and the shot came out un-dutched with no clue why. It is now
  added outside the gate; everything else in that block is unchanged.
- **Tilt was measured relative to the lens elevation at Centre.** Subtracting a
  fixed number from an angle is not a rotation, so the camera stopped being
  rigidly attached to the phone and the aim walked away from it as you panned.
  Measured: centre 20 deg off level and pan 90 deg, and the shot is 20 deg out;
  at 40 deg off it is 40 out. Tilt is now the absolute lens elevation, which is
  0.00 deg out from any centring pose up to 60 deg off level. Centre still sets
  the pan and the horizon - those are constant rotations, so they keep the rig
  rigid - and the app now says to hold the phone level, with a live readout of
  how far off it is.

With both in, the reported case is exact: filming in landscape and turning the
phone to portrait moves the aim by 0.000 deg and rotates only the horizon, at
every facing - which is what a real camera body does. Note what that means on the
recording side: the game still renders in the monitor's landscape aspect, so a
90 deg roll gives you a rolled landscape frame, not a portrait one. Shooting a
genuinely vertical 9:16 clip needs Assetto Corsa itself running at a portrait
resolution.


### Phone axes fixed at the source (2026-08-25)
- **The phone's pitch and roll were swapping into each other depending on which
  way you faced.** Both apps decomposed the phone's rotation with a world-frame
  euler chart, which reads pitch and roll about FIXED horizontal axes of the
  calibration frame. Sweeping that path through a simulation shows what it
  actually did: tilting the lens up 30 deg came out as **roll -30 with pitch 0
  at every facing**, and turning the phone from portrait to landscape came out
  as **pitch 90** — the camera going somewhere unrelated to where the phone
  went. No Swap/Invert setting can fix that, because the error depends on the
  pose, not on a sign. `Swap P/R` and `True axis` are gone rather than re-tuned.
- **Replaced with the way a camera head actually moves**, measured from the lens
  itself: pan = the lens azimuth about gravity, tilt = the lens elevation, roll =
  the twist of the phone about the lens versus horizon level. Each channel is a
  different physical axis of the same rig, so a motion about one axis can only
  land in that axis's channel — at any facing, in any grip. Point the lens
  somewhere and the in-game camera points there. Validated by a swept-rotation
  simulation: 24/24 cases exact, including grip changes mid-move and three full
  turns. Pan and roll are integrated from the shortest step, so they are
  continuous and unbounded (no +-180 seam, no pole flip, so the separate
  gimbal-unwrap pass is no longer needed); tilt is absolute elevation and so
  cannot drift or fold over.
- **New `"cv"` field in the packet (convention version).** The receiver was
  hard-flipping pitch and yaw to compensate for the old apps. It now applies that
  flip **only to senders that do not report `cv >= 2`**, so a new app and an old
  APK can both talk to the same mod and neither ends up inverted. The Phone Gyro
  tab shows which convention the connected phone is using.
- **Roll has a mode now** (in the phone app): 1:1 like a real camera, damped like
  a loose gimbal, or locked so the horizon never tilts.

### Viewfinder: the stutter had three separate causes, all fixed
- **Every datagram was being sent twice** (`DUP = 2`) as crude redundancy. Wi-Fi
  loss is bursty, not random, so both copies were usually lost together — it
  doubled the bitrate for almost no benefit, and the extra load made loss more
  likely.
- **Nothing paced the sender.** A keyframe left as ~35 back-to-back datagrams,
  which overruns the driver queue and the access point, so the single frame the
  stream depends on most was the one most likely to be shredded. Frames are now
  paced at 1.8x the measured stream rate.
- **The phone never noticed a missing frame.** A lost fragment meant that unit
  never completed, but the next one decoded anyway — predicted from a picture the
  decoder never received. That is what the smearing was: not dropped frames,
  corrupted ones. A gap in the sequence now stops decoding until a clean frame
  and asks the PC for one.
- **A restarted video server used to kill the viewfinder until the app was
  reinstalled**: the phone only ever accepted increasing sequence numbers, so a
  server starting again from 1 looked stale forever. A backwards jump is now read
  as a new stream.
- **Default capture is MJPEG.** Every JPEG frame is independent, so a lost packet
  costs exactly one frame and the next is already clean — there is no reference
  chain to corrupt and no keyframe to wait for. It also encodes on the CPU, so it
  never competes with OBS or ShadowPlay for the NVENC session. H.264 is still
  there (`Efficient`) for a clean 5 GHz link. Measured on this machine:
  Balanced 854p30 ~6.5 Mbit, Sharper 1280p30 ~16 Mbit, Smoother 768p24 ~3.2 Mbit.
- **The capture-mode buttons never did anything.** The four names the UI sent
  (`phone`, `nvenc`, `software`, `low`) were not modes the video server
  implements, and the setter rejected all of them — including its own default.
  Real modes now, and old saved values migrate.
- **"Restart viewfinder" never worked either.** It ran the `.py` as if it were a
  `.bat`, killed every `ffmpeg.exe` on the machine, and left the Python parent
  holding the single-instance port, so the relaunch it fired immediately exited.
  Switching mode now just writes a file the running server re-reads, which
  restarts only the encoder — no process hunting at all.
- The video server now ships inside the app folder instead of being found on a
  developer's Desktop.

### Link
- **The phone's WebSocket had Nagle switched on.** Nagle holds a small write
  until the previous segment is acknowledged — which is exactly this traffic —
  so 60 Hz motion could arrive in clumps instead of evenly. `TCP_NODELAY` plus a
  responsive-data service class (higher Wi-Fi priority, so control packets are
  not queued behind the video) and a short keepalive.
- **Zoom could not be released on Android.** The app omitted `fov` when it was 0,
  so the mod stayed pinned to the last non-zero value. It is always sent now, on
  both platforms.

### 6DOF back on — but iPhone only, and the viewfinder went silent + AC-only
- **6DOF re-enabled for the iPhone.** The receiver's whole 6DOF path (tx/ty/tz
  parse, One Euro filter, the operator rig in `modulos/sixdof.lua`) was intact;
  it had been switched off in one place — the packet parse hardcoded
  `is6DOF = false`. It now reads the packet's `"6dof"` flag again
  (`is6DOF = (sixdof ~= nil)`). The iPhone app (v1.1) sends position via ARKit
  world tracking (LiDAR-assisted on the 13 Pro); the Android app no longer sends
  it, so **Android stays gyro-only automatically** and only the iPhone drives
  position. Still gated behind the existing **Enable 6DOF** toggle in the Phone
  Gyro tab (default off) — tick it once to use it.
- **Viewfinder is now silent and captures only the game.** The auto-started PC
  server defaults to a new `ac` mode: `gdigrab title=Assetto Corsa` (only the AC
  window, so no second monitor / desktop) encoded with hardware H.264 (NVENC,
  low-latency, 1600-wide @60) — much sharper and far less delay than the old
  MJPEG desktop grab. It launches in a hidden window so it never steals focus
  from the game. Requires AC in **borderless** (gdigrab cannot grab exclusive
  fullscreen). `viewfinder-server.bat` gained the `ac` mode.

### New tab: a butterfly knife in your hand
First person viewmodel, off by default, in its own tab. It does not depend on
walking mode, so it works on foot or in the car.

The model is the real CS2 butterfly knife and a CS2 motorcycle glove, pulled from
the game files. Five rigid pieces in one KN5: blade, two handles, latch, hand. The
flip is not a baked animation. It is two angles, the blade turning on the safe
handle's pin and the bite handle turning on the blade's pin, which is how a real
balisong moves. Those angles live in a seven row table in `modulos/knife.lua`, so
retiming the flip is editing numbers and reloading the script.

The two pivot pins were taken from the geometry rather than eyeballed: for each
handle, the centre of the vertices sitting inside the blade's tang. They came out
symmetric across the blade and at the same height, which is what a balisong pivot
pair looks like.

Two things cost a rebuild before it rendered, both worth writing down:

- **Mesh nodes must not share a name with a bone.** The first export named the mesh
  wrappers `blade`, `handle_bite` and so on, matching the bones they are skinned
  to. The model loaded and every bone resolved, and nothing drew, because the skin
  binds by name and picked the mesh node. They are `MESH_*` and `SUB_*` now.
- **Rows of a `mat4x4` are `vec4`, not `vec3`.** Assigning a vec3 throws at runtime.
  The `side`, `up`, `look` and `position` fields are the same axes as vec3 and read
  better anyway.

Rough edges, all listed because the knife is a base and not a finished thing: the
hand is attached in its bind pose so the fingers do not close on the handle yet, the
glove has no colour map (CS2 composites it at runtime), and the flip timing has not
been tuned in game.

Settings persist by name through the generic storage below, so the knife needed no
schema entries of its own.

### The CS 1.6 combat layer is gone
Removed at the author's request. Not disabled, not hidden behind a flag: deleted.

Out went `modulos/cs16.lua` and the six modules under `modulos/cs16/` (weapons data,
weapon state machine, entities and hit testing, GoldSrc movement, audio, HUD), the
six wiring points in the main file (require, init, the update call after walking
movement, the HUD draw, the tab, and the 3D pass), and 60 MB of assets it owned
alone: `models/weapons/`, `models/enemies/`, `models/anims_cs/` and `sfx/`.

The CS 1.6 tab is gone from the tab bar. Nothing else moved. The layer was off by
default and every entry point was already guarded, so no other feature was reading
from it.

Any `cs16_*` values still sitting in your saved settings are inert and nothing
reads them anymore.

### Rebinding onto a key that was already taken used to happen silently
Capture wrote whatever you pressed straight into the bind table without checking
whether another action was already there. Both then fired on that key, and the
one you did not want usually won the argument, which reads as "the rebind didn't
work". Nothing warned you at the time and nothing showed you afterwards.

Capture now looks first. Land on a free key and it binds as before, no extra
click. Land on a taken one and it stops and names what is already there, using
the readable label from the tab rather than the internal name, then gives you
three explicit choices:

- **Move it here** unbinds the other action and gives this one the key, so
  nothing ends up shared. The action that lost it shows as None, so you can see
  what happened instead of guessing later.
- **Share it** leaves both on the key. Both will fire. Sometimes that is what you
  want, so it stays available.
- **Cancel** leaves the bind exactly as it was.

Nothing is picked for you and nothing is blocked.

The Keybinds tab also lists collisions already saved in your config at the top,
including ones made before this check existed, naming both actions on each key.
It draws nothing when there are none.

One overlap ships on purpose and is excluded from all of this: F5 cycles camera
motions and Shift+F5 disables them, same key, split by the modifier in code. That
is the only duplicate in the shipped defaults, checked across all 42 bound keys.

### Your keybinds and 136 settings were being thrown away on every exit
A user asked whether keybinds not saving was a known issue. It was not known, and
it was worse than one bug. Persistence here worked by hand: `ac.storage{}` holds a
fixed list of declared fields, and `Settings.save`/`Settings.load` copy values one
line at a time, by name, in both directions. Anything not present in all three
places was silently dropped when the game closed.

Counted against this build:

- **104 keys the UI reads and writes that were never in the layout.** Among them
  the phone gyro IP and port, so the IP had to be typed in again every session.
  Also hide cursor, car collision, the whole third-person camera block, aim
  friction, and 13 avatar animation fields.
- **32 keys declared in the layout and then never copied either way**, so they
  always came back at default no matter what you set. Fatigue, exit offset, step
  shake, running pitch, tracking roll.
- **Every keybind.** Those are dynamic keys, written as `"keybind_" .. name`, and
  a fixed layout cannot hold a name it does not know in advance. No rebind ever
  survived closing Assetto Corsa.

Adding 136 names to three places by hand would have fixed today and broken again
on the next feature, since that is exactly how this happened. So the whole config
now gets copied generically into the free-form side of `ac.storage`, which takes
any key name. Values carry a type tag so a number comes back a number and a
boolean comes back a boolean, keys are prefixed so they cannot collide with a
declared field, and an index key records what was written. Save writes only the
keys whose value changed, so dragging a slider touches one entry instead of four
hundred.

Two things are deliberately left out. Session state, so the mod no longer risks
switching itself on and grabbing the camera at session start. And nested tables,
which the per-motion CineMotion settings already handle themselves.

The generic read runs last on load, after the per-key reads. That ordering also
kills a quieter bug: those reads use `or default`, which turns a genuinely saved
`false` or `0` back into the default. The saved value now wins.

Nothing to do on your side. The first launch after updating still reads the old
storage, and from the first save onward everything persists.

### There were three separate ways to freeze the FOV, not one
The discrete-zoom fix below was real but it did not close the field report: the
same user came back saying the focal length presets did nothing either, and those
already cleared discrete mode. So the block had to be downstream of both. Two more
causes, both proven in code, both able to kill every FOV control at once.

- **A phone that stopped talking kept driving the zoom forever.** The zoom update
  pinned targetFov to the phone's value on the test `phoneGyroEnabled and last fov
  > 0`. The stale-data path in phone_gyro only flips `connected` after 1.5s of
  silence; it never cleared `phoneFov`. Only pressing Disconnect did, and nothing
  else in that reset list is left behind like this - orientation, velocity, movement
  and the 6DOF translation all zero themselves. So closing the phone app, losing
  wifi or letting the phone sleep left a live-looking zoom value that overwrote
  targetFov every frame, and from then on nothing on the PC could move the FOV:
  not the slider, not the presets, not the wheel. Now the phone only drives zoom
  while `isConnected()` is true, and the stale path clears the cached fov.
- **"Enable Full FOV Range" is a 45 degree floor and never said so.** When off,
  the camera write clamps to 45-90. Worked out against the app's own presets: 7 of
  the 9 camera lenses (35mm and every longer one), 4 of the 6 phone presets (2x
  and up) and 5 of the 6 scroll steps all resolve to exactly 45.0 degrees. Clicking
  50mm, 85mm, 135mm, 200mm and 400mm in a row produces five identical frames. The
  tooltip claimed "Zoom always works!". It now describes the clamp, and the tab
  shows a red line when the box is off.

### The FOV row now shows what the camera actually got
Everything in View & FOV was the requested value. Added a readout of the live
`sim.cameraFOV` next to it, green when they agree and red when they do not, plus a
"Why:" line naming the gate that ate it (camera not grabbed, full range off, phone
gyro driving, locked zoom, discrete step, dolly playback). A user reporting "the
FOV does nothing" can now screenshot the answer instead of the symptom.

### The FOV slider in View & FOV did nothing, and one wrong division was why
Reported from the field as "the mod activates, I can look around, but the camera
tab does not change anything". It reproduces on any build going back to v1.5.4,
which is why reinstalling and rolling back did not help anyone.

- **`math.min(1.0, discreteZoomSpeed / dt)` divided where it should have
  multiplied.** The default 0.15 at 60fps gives 8.98, and the min() pinned the
  interpolation factor at exactly 1.0. Measured across the range: 1.000 at 30,
  60, 144 and 240fps. So the "smooth transition to discrete zoom target" was a
  hard `targetFov = discreteZoomTarget` executed every single frame, and it only
  stopped saturating below about 20fps. Now `1 - exp(-dt * rate)`: 0.2212 per
  frame at 60fps, 0.0989 at 144, 0.0606 at 240, and a 0.5x to 1x step settles in
  0.283s at any of them. The slider keeps its direction (higher = snappier), so
  saved discreteZoomSpeed values still mean what they meant.
- **The consequence nobody could see:** while discrete mode was armed, anything
  else writing targetFov was overwritten on the next frame. The FOV slider writes
  targetFov. The focal length preset buttons happened to also clear
  discreteZoomMode, so those kept working and the slider did not, which is what
  made it look like a display bug rather than a dead control. The slider now
  clears discreteZoomMode and zoomVelocity the same way the presets do.
- **What armed discrete mode in the first place:** one scroll of the wheel, and
  `cfg.scrollZoomDiscrete` turns itself on simply by drawing the tab, because
  `checkboxWithReset(..., cfg.scrollZoomDiscrete ~= false, ...)` writes its own
  result back into cfg and `nil ~= false` is true. Nothing clears the flag on
  walk mode activate, so it stuck for the rest of the session.

### Locked zoom had a silent ceiling at 63 degrees
Locked zoom clamps targetFov to the phone lens range, which at 16:9 with the
default hFOV presets is 9.04 to 63.09 vertical. The slider ran to 120 and the
app's own defaults sit at 70/76, so the entire top third of the slider was a dead
band that snapped back with no explanation. The slider now takes its bounds from
the same clamp and says so in a line under it. The clamp itself is unchanged: it
is a deliberate feature, it just needed to be visible.

### Six zoom settings were never actually saved
`scrollZoomDiscrete`, `lockedZoom`, `aspectAwareZoom` and the six `zoomHFOV_*`
presets were read by the UI and by the zoom update but did not exist in the
storage schema, so `saveWalkingSettings()` silently dropped them and they reset
on every launch. Turning locked zoom off never survived a restart, and editing
the 0.5x/1x/2x/3x/5x horizontal FOV values was lost on exit. All nine are now in
defaults, save and load. Booleans use `~= false` rather than `or true`, which
cannot write an OFF back to storage (same trap as the flashlight settings).

### 6DOF: the axis maths was wrong, which is why it never sat still
The rig was fine. What fed it was not. Three separate things, all measured
rather than guessed, all fixed.

- **The calibration heading was computed with the wrong convention.** ArTracker
  extracted a yaw angle with `atan2(2(wy+xz), 1-2(y*y+z*z))`. That denominator
  belongs to a Z-up system; ARCore's world is Y-up and wants `1-2(x*x+y*y)`. The
  two agree only when the phone is flat and unrolled, and the app runs in forced
  landscape, which is 90 degrees of roll by definition. Simulated against real
  holds: true heading 30 degrees read as 90, heading 180 read as 151, and
  pitching the phone 20 degrees up moved it again.
- **The rotation was then applied with the wrong sign** (R_y(+yaw) where the
  projection wants R_y(-yaw)), which mirrors the result even when the angle is
  right. Isolated: at heading 90, where the extracted angle happened to be
  correct, "hand 30 cm right" came out as 30 cm LEFT.
- Together: at heading 30, moving the hand 30 cm right produced 15 cm left plus
  26 cm forward. Aiming 20 degrees up turned "right" into almost pure "forward".
  And because the calibration is redone on every re-anchor - every flicker of
  tracking - the control axes rotated mid-shot with nothing on screen to say so.
  Fixed by dropping the angle entirely: the calibration now stores the operator's
  right and forward as vectors and projects the delta onto them. No convention to
  pick, no sign to invert, no singularity in landscape. Verified across headings
  0 to 270 and pitches -35 to +20: every hold maps 1:1 to within 0.0001 mm.
- **The mod applied the offset in the live camera basis**, which double-counted
  rotation: the phone already reports where it physically is, so re-projecting
  through a basis that turns with the aim swept a held 30 cm offset through a
  42 cm arc on a 90 degree pan, and pitching down tilted "hand up" into the
  screen. It also inherited `right = up x look` from the tracking shake, which is
  the mirror of right in this mod's convention (yaw grows to the LEFT here) -
  invisible on symmetric shake, an inverted X axis on a 6DOF rig. Now applied in
  the operator frame: horizontal heading with the phone's own aim removed, plus
  true vertical. Turning the character carries the rig; panning the phone no
  longer rotates the axes underneath it.

### 6DOF tuning, with the numbers written down
- **Spring 10.07 Hz -> 4.00 Hz** (stiffness 320 -> 50.5, damping 9.20 -> 3.62,
  zeta stays 0.90). At 10 Hz it was not filtering anything it claimed to: a
  second-order low pass at that corner passes 0.99 of a 1 Hz input, 0.94 of 3 Hz
  and 0.85 of 5 Hz, and ARCore's noise and drift live entirely in that band. It
  bought 40 ms of latency and rejected nothing. At 4 Hz the same points are
  0.98 / 0.70 / 0.43. Measured cost: a 20 cm hand move at 2 m/s now lands in
  200 ms instead of 117 ms. Both numbers are on sliders.
- **Re-anchor detection is a speed, not a distance.** It was a flat 35 cm, which
  only caught catastrophic jumps while ARCore's ordinary loop closures (5 to
  20 cm) went through as real movement - an instant 20 cm whip. Now 3.5 m/s
  converted per pose interval, floored at 8 cm: nothing a hand does exceeds it,
  and a re-anchor is instant, so the two never overlap.
- **New: Drift cancel (s) slider, default 0 = off.** High-pass on the phone
  position. VIO has no absolute reference and wanders slowly, and no spring can
  separate that from a slow deliberate move because both are low frequency -
  subtracting a slow baseline is the only thing that can. Off by default because
  it costs exactly that: slow deliberate moves. For dark or blank rooms.

### 6DOF: the camera no longer stays dead after one hiccup
- ARCore does not reclaim a camera it lost: it keeps the session alive and keeps
  reporting CAMERA_UNAVAILABLE forever. Measured on the A56: the camera opened
  for 3.7 seconds and the app then streamed "not tracking" for 38 hours straight,
  with the only symptom a line of text in the settings panel. There is now a
  10 Hz watchdog that pauses and resumes the session after 2 seconds stuck.
  Deliberately does not fire on the environment failures (too dark, no features):
  those clear on their own and restarting would only throw the tracking away.
  Recovery count shows in the status line as `R:n`.

### Viewfinder fixed (in-app PC screen) + one ARCore pipeline, no invented position
- The in-app viewfinder showed nothing. Root cause, proven with a heartbeat log:
  the video used a bottom SurfaceView whose native surface was never created on
  this phone (surfaceCreated never fired, isValid() stayed false forever), so
  the hardware decoder had nowhere to draw. The PC encoder was fine the whole
  time - a local TCP probe pulled a correct H.264 stream (AUD/SPS/PPS/IDR,
  keyframe first) off ffmpeg's :9877. Fixed in the shared phone app (v7.41) by
  switching to a TextureView, which always delivers its surface. Verified end to
  end: "surface READY" -> "connected" -> stream. This app and Mobile Cam share
  one phone APK, so the single fix covers both.
- 6DOF receiver conflict removed. Two layers were both deciding what happens on
  tracking loss: phone_gyro.lua decayed the translation to zero while sixdof.lua
  was built to freeze, and the receiver ran first so the camera slid home. The
  receiver now only REPORTS the loss (clears has6DOF immediately); the rig owns
  the behaviour and freezes, then resumes in place. It also stopped running its
  own One Euro + velocity extrapolation on the pose - two smoothers in series
  with the spring added lag, and the extrapolation invented position between the
  30 Hz ARCore frames. The receiver now passes the real pose straight through
  and the spring is the single filter.
- Dead code removed: the orphan `_disabled_arcore/ArTracker.kt` copy in the APK
  project. ARCore now lives in exactly one place (ArTracker + the MainActivity
  GLSurfaceView); the Viewfinder overlay path is documented as orientation-only
  by construction (an overlay window cannot host ARCore's GL context).

### Phone camera no longer spins when it hits the end of an axis (gimbal wrap)
- Panning with the phone past half a turn from the calibration point made the
  camera snap a full turn the other way, and tilting past vertical flipped the
  view over the top. Same root cause on both: euler angles are a chart with
  seams (atan2 folds at +-180, asin at +-90) and the app was streaming them as
  absolute values, so crossing a seam looked like a 360 jump - exactly like
  arrowing down a list and landing back on the first item.
- The app (v7.39) now integrates the shortest delta per sample instead of
  reading the absolute angle, so the stream is continuous and unbounded: turn
  the phone three full circles and the camera turns three full circles. The
  pole crossing is detected for what it is (yaw AND roll jumping ~180 while the
  quaternion barely moved) and swallowed. **The new APK is required for this
  half of the fix.**
- Mod side: the final aim pitch now stops at 89.5 degrees instead of going over
  the top. One degree past straight up, `cos(pitch)` changes sign and the look
  direction mirrors - the view appeared to spin 180 on its own. Yaw has no
  limit at all.
- Calibrate now also drops the interpolation sample pair and the velocity
  history, so recentering no longer sweeps the camera through the old offset
  for one frame.

### 6DOF retuned to VR-controller behaviour (1:1), and it now FREEZES on tracking loss
- Position is 1:1 with the hand by default, bounded only by the multipliers: move
  the phone 50 cm and the camera moves 50 cm (measured 0.497 m, the 3 mm deadzone
  being the difference). New "VR 1:1" rig is the default; the old weighted feel is
  still one click away as "Handheld".
- Tracking loss now FREEZES the position instead of easing it back to centre, and
  a recovery RESUMES IN PLACE. Previously the offset faded home on a dropout and
  the reference re-zeroed on return, which is a teleport in both directions. The
  last good displacement is held, and when tracking comes back the reference is
  rebuilt so the new pose reproduces exactly that displacement - verified against
  a simulated 9 m ARCore re-localisation, which now moves the camera 0.00 m.
  Orientation is unaffected throughout: it comes from the IMU, which does not
  care whether the camera can see anything.
- Spring retuned from ~7 Hz to ~10 Hz (zeta 0.91): catching a fast hand move went
  from 83 ms to 67 ms. At 7 Hz it measured as lag rather than as weight.
- Expo defaults to 0 on the translation axes, because a curve is the opposite of
  1:1. It is still there if you want it.
- Protocol v6: the phone now reports ARCore's TrackingState and, when it is not
  tracking, the reason. Sent even when no pose goes out, so the panel can say
  "too dark" instead of just showing nothing. Needs APK v7.40.
- 24 offline checks now cover 1:1 fidelity, latency, freeze, resume-in-place and
  the re-localisation case, on top of the previous axis/drift/jitter set.

### Phone Gyro 6DOF: the phone is now a spatial controller
- Moving the phone through space moves the camera. This is the POSITION half of
  Phone Gyro and it lives in the Phone Gyro tab, next to the aim settings it
  belongs with - not in a tab of its own. Rotation still comes from the existing
  aim path; nothing about how the phone aims the camera has changed.
- New `modulos/sixdof.lua`. Each of the six axes is an independent
  mass-spring-damper, `m*x'' = k*(target - x) - c*x'`, where the TARGET is where
  your hand is and the output is where the camera is. That single choice is what
  makes the feature usable at all:
  - tracker jitter cannot reach the camera, because a mass cannot vibrate at
    tracker noise frequency
  - the camera cannot teleport, because a spring has finite speed
  - losing tracking returns it to rest instead of freezing an offset there
- Parameters are the real physical ones (mass in kg, stiffness in N/m, damping
  in N.s/m), so mass genuinely matters: a heavier camera on the same spring lags
  more. Natural frequency, damping ratio and settle time are DERIVED and shown
  live under the sliders, instead of being a second set of knobs fighting the
  first. Tuned for low latency by default - the spring is stiff and the input
  smoothing is 30 ms, not a heavy filter.
- Per axis, all independent: enable, invert, amount, clamp, offset, deadzone,
  expo, sensitivity, smoothing, mass, stiffness, damping and stick travel.
- Offsets sit OUTSIDE the spring and OUTSIDE recenter, because they are where
  you want the camera placed, not part of the tracked movement.
- Rigs (Handheld, Shoulder, Chest, Body Cam, Tripod, Crane, Drone, Raw 1:1) are
  named sets of the same sliders. Applying one writes those values into the
  visible controls; there is no hidden second code path.

#### Position source
- ARCore translation is used as an ABSOLUTE position source. Nothing integrates
  acceleration to invent a position - that drifts without bound, so it is
  deliberately not done, and the code says so where you would be tempted to.
- The phone only sends position while its own "6DOF" checkbox is ticked and
  ARCore has tracking (which needs light and texture to lock on). The tab now
  states plainly whether position is arriving instead of leaving you guessing,
  and orientation keeps working either way.
- AR re-anchoring is absorbed: a jump larger than 35 cm between consecutive
  poses is ARCore moving its own origin, not your arm, so the reference is
  shifted by the same amount and the camera does not move at all. This is the
  root cause of the old "6DOF broke everything, the camera flew away".

#### Rotation - and why absolute orientation is never mixed in
- The rotation axes add optional wrist lag driven by the phone's angular RATE,
  never by its absolute angle, which is already applied upstream - mixing the
  two would double-apply the orientation. Ships at amount 0, so the existing aim
  feel is untouched until you dial it in.
- Orientation fusion stays where it already was and was not rewritten: the phone
  fuses gyro + accelerometer (GAME_ROTATION_VECTOR, no magnetometer, which is
  what keeps yaw from drifting indoors), calibrates by quaternion multiplication
  and converts to Euler once, on the device, as the final step. The debug panel
  now shows that live quaternion.

#### Recenter
- Calibrate now recentres orientation and 6DOF position together, so "this is my
  neutral pose" means the same thing for both halves. It cannot jump: recentring
  moves the reference point, not the camera. Configured offsets are untouched.

#### Verified offline
- `sixdof.lua` runs standalone under a stubbed API, and 21 checks cover the audit
  list: axis directions (right/up/forward all non-inverted), axis independence
  (crosstalk exactly 0), frame-rate independence (15 vs 240 fps agree to 4
  micrometres), no drift over a 30 s hold, 3 mm of tracker noise producing zero
  movement, a 5 m AR re-anchor producing zero movement, return to rest on
  tracking loss, recenter behaviour, offsets surviving recenter, clamps, the
  invert flag, and rate-driven wrist lag trailing rather than leading.
- Found and fixed during that pass: the rotation axes were being faded by the AR
  position staleness, which would have silently disabled wrist lag for everyone
  running without ARCore. Staleness now gates the translation axes only.

#### Recorder
- Takes record the six rig outputs per frame and replay them exactly rather than
  re-simulating, since the tracker will not reproduce the same input twice.
  During playback the integrator is bypassed; returning to live control re-arms
  it in place with no jump.

#### Compatibility
- Everything is behind `cfg.sixdofEnabled` (default off) AND requires Phone Gyro
  to be connected. Walking Mode, Tracking, Aim, Recorder, Replay, mouse, gamepad
  and keyboard paths are untouched when it is off. The rig's rotation is ADDED
  after tracking resolves its aim, so the two coexist instead of overwriting
  each other.
- Optional stick/keyboard control of the rig: numpad by default (nothing else in
  the mod uses it), virtual-key codes in the config so nothing is hardcoded, and
  the gamepad only drives the rig while a held modifier is down so movement and
  look keep working.

### Flashlight settings now actually stick (O-key phone flash fix)
- Fixed the reported bug where the O-key phone flash ignored your flashlight
  settings and fired with the default look (sharpness, spot, brightness, etc.).
  Root cause: the Flashlight tab wrote straight into the module's live config,
  which was only persisted by the "Save All Settings" button - and walking-mode
  init reloads the module config from the saved values, silently reverting any
  unsaved tweak to defaults. The photo blink then captured with that reverted
  light. The tab now autosaves on change, so what the sliders show is what the
  flash (and the lantern) uses.
- Flash Style, Flash Intensity, "Take Screenshot on Flash", the phone flash key
  and the SOS timings were never written to storage at all, so they reset every
  session even after Save All. Added to the storage schema, save and load.
- Light Color, Camera Response, Hand Tremor and Running Tilt were in the same
  boat (tab-only, never persisted). Also added.
- Saving SOS as the flash style loaded back as Lantern (the load-time legacy
  remap maps 3 to Lantern; saves now use the legacy 4-value encoding so old and
  new configs both load right).
- "Enable Shadows", "Show in Reflections", "Walking Sway" and "Idle Sway" could
  never be saved or loaded as OFF (classic Lua `x or true`, which is always
  true). Turned them into proper nil-safe checks.
- Saved flashlight values now reach the module on the first frame instead of on
  the first walking-mode init, so the Flashlight tab no longer shows defaults
  until you go on foot once.
- Corrected the footer hint in the Flashlight tab: the phone flash key is O,
  not F (F had been reassigned to camera height long ago).

### Keybinds (AZERTY / non-US layout fix)
- You can now bind ANY key again, including the national / OEM keys AZERTY and other
  non-US layouts rely on (the ² ù ^ $ * < ! row, etc.). Key capture was reading the
  keyboard through ImGui (`ui.keyboardButtonPressed`), whose key map silently drops
  those OEM keys, so pressing them during "Press key..." registered nothing even though
  the mod reacts to them fine at runtime. Capture now reads raw Windows virtual-key
  state via `ac.isKeyDown` — the exact same source the binds use when they fire — so
  anything the mod can react to can also be captured. Edge-detected against a snapshot
  taken when capture opens, and mouse buttons are skipped so the click that starts
  capture isn't grabbed as the bind. Reminder: movement (Move Forward/Left/…) is fully
  rebindable in the Keybinds tab, so AZERTY users can set it to ZQSD.

### Phone Camera USB
- USB connect no longer silently fails when Android's `adb` isn't on PATH (the usual
  "WiFi works, USB doesn't" case). The app now looks for adb shipped alongside it
  (`bin/adb.exe`), then the Android SDK's default location, then PATH, and runs the
  forward from whichever it finds. If none exist it says so in the status instead of
  spinning on "Connecting..." forever. Ship `bin/adb.exe` with the app for zero-setup USB.

### New: CS 1.6 Special Edition (experimental combat layer, OFF by default)
- Scaffolds a first-person shooter mode on top of the walking primitives. New "CS 1.6"
  tab; enable there, walk mode must be on and you must be on foot. Everything is gated
  behind `cfg.cs16_enabled` (default false), so the base mod is unchanged until toggled.
- New modules under `modulos/cs16/`: `weapons_data` (8-gun CS table - knife/USP/Glock/
  Deagle/AK-47/M4A1/AWP/HE with real damage, RPM, mag, reload, per-weapon move speed),
  `weapon` (hitscan fire, CS spread+recoil model, ammo/reload/switch), `entities`
  (target-agnostic dummies with an authoritative ray-vs-capsule hit test + headshot
  zones - NOT the scene raycast, so we own hit id/zone and it ports to bots/PvP later),
  `movement` (faithful GoldSrc controller: 250 u/s cap, 20.32 m/s^2 gravity, 6.8 m/s
  jump, 0.762 m/s air-wishspeed clamp for real air-strafe), `audio` (pooled
  `ac.AudioEvent.fromFile` wrapper, degrades to silent if the API is unavailable), `hud`
  (CS corner layout: dynamic green crosshair that expands with spread, health/armor
  bottom-left, ammo bottom-right, money top, killfeed). Orchestrated by `modulos/cs16.lua`.
- Reuses existing primitives: `raycast.castRayImmediate` for wall occlusion,
  `avatar_advanced` for enemy bodies (fallback capsule if unavailable), the AIM vector
  math and `state` from the walking system.
- Loaded behind a plain `pcall` (not `_safeRequire`) and every entry point is guarded, so
  a fault in the combat layer can never set `_initError` or blank the app.
- Placeholder synthesized SFX in `sfx/` (gunshots/reload/etc). Drop real CS 1.6 `.wav`
  files with the same names to replace them. Controls: WASD move, Space jump, Ctrl
  crouch, Shift walk, LMB fire, R reload, 1-8 weapon, T respawn targets.
- Milestone 1 scope: solo weapon feel + shootable dummy targets (the "does it work"
  proof). Bots and PvP reuse the same target-agnostic damage model later.

#### Fixes (first playtest)
- HUD was invisible: it was hooked into `windowCrosshair` (WINDOW_1), a separate overlay
  app the user hadn't enabled, so it never ran. Moved the HUD draw into `windowMain`
  (WINDOW_0, always enabled) right after `EmoteWheel.render()` - the mod's proven
  fullscreen-overlay path.
- Movement felt too fast: added `cs16_moveScale` (default 0.6; 1.0 = authentic 250 u/s)
  with a "Move speed" slider. Applied to the per-weapon cap.
- Added a first-person weapon viewmodel (procedural wireframe rifle, walk bob + recoil
  pushback; toggle "Show weapon"). Placeholder until a real KN5 gun model is ported.
- Reworked placeholder SFX: punchy broadband gunshots (attack + low-passed noise blast +
  fast pitch-drop thump + soft-clip) instead of the tonal buzz. Still placeholders.
- Added one-shot diagnostics + error surfacing in the 3D pass (`[CS16]` log lines) so
  swallowed render/viewmodel errors and the live target count are visible in the CSP log.

#### Real audio (playtest 2)
- Replaced the synthesized placeholders with REAL CS:GO weapon sounds (from the
  sourcesounds/csgo loose-wav set): per-weapon fire (AK/M4/USP/Glock/Deagle/AWP),
  concatenated real reload sequences (mag-out + mag-in + bolt/slide), real knife slash.
  Also pulled the CS:GO knife inspect/deploy swishes (knife_inspect1/2, knife_deploy)
  for the upcoming spinning-knife viewmodel. NOTE: Valve copyright - local/test use only;
  a free release needs CC0/CC-BY replacements (candidates identified).
- Added drawHud instrumentation (`[CS16] drawHud reached … / Hud.draw ERROR`) to find why
  the HUD is still invisible after moving it to windowMain.

#### Playtest 3 - nothing renders (targets/HUD/weapon invisible, movement + sound OK)
- Root cause for invisible TARGETS: `Entities.render` called `AvatarRenderer.draw(id, …)`
  which returned success under pcall but drew nothing for our synthetic entity ids (no
  registered avatar/anim), so the guaranteed-visible fallback never fired. Fix: always
  draw the fallback capsule (render.debugSphere/Line), tinted HDR green so it blooms.
- Fixed VIEWMODEL placement: it built the camera basis from `state.yaw/pitch` (lags, not
  the eye at render time). Now uses `ac.getSim().cameraPosition/.cameraLook/.cameraUp` -
  the correct render-time camera - and a brighter gunmetal color.
- Added a temporary DEBUG BEACON (gated on walk mode only, independent of the CS toggle
  and persistence): magenta HUD bars + a red sphere/green pillar/label 4 m ahead. Proves
  whether render.debug* (3D) and the windowMain ui overlay (2D) actually display, and
  logs the live walk/cs16/showHud state each ~2 s. Remove once rendering is confirmed.
- Confirmed persistence is NOT broken: ac.storage hashes key names (ini shows numeric
  hash keys), so cs16_* values do persist - earlier "no cs16 keys" grep was a false alarm.
- Real CS:GO weapon/knife sounds now wired (replacing the synths).

#### Real 3D models (KN5) - no more debug wireframe
- Weapon viewmodels are now real loaded KN5 models (ac.SceneReference:loadKN5()), driven
  camera-relative from ac.getSim().cameraPosition/.cameraLook each frame in the lower-right:
  - ak47.kn5 - Valve official OBJ, decimated to 8000 tris, scaled 0.70 m (all guns use it
    for now). Flipped 180 about up because the AK is authored with its muzzle at local -Z.
  - knife.kn5 - modeled blade + handle; SPINS around its blade axis (the CS inspect twirl),
    with the CS:GO inspect swishes playing along.
  - Wireframe stays as a graceful fallback if a model fails to load.
- Enemies are now real 3D humanoid dummies (dummy.kn5, modeled low-poly, 1.79 m tall,
  feet at origin), loaded per target, standing at the spawn position facing the player.
  Debug capsule kept as fallback, so nothing regresses.
- Conversion pipeline (reusable): Blender 5.0 headless + a KN5 v6 writer derived from the
  proven export_pw_kn5.py (single-bone DRIVER:DRIVER rig, solid generated-PNG textures);
  every output validated by a round-trip parser (0 leftover bytes) before shipping.
- Removed the debug beacon (render pipeline confirmed working in-game by screenshot).

#### Full polish: animated TR/CT, chicken, arms, radar, crouch
- Enemies are REAL animated CS characters now: Terrorist + Counter-Terrorist (Quintenps/
  CSGO-Models, real VTF textures decoded), retargeted to the mod's 55-bone DRIVER:RIG_*
  skeleton (byte-identical to CJ) so the ksanim clips drive them - breathing idle when alive,
  cj_death_from_the_front when killed. Teams alternate by id. Different models than the player
  avatar (forza_driver), so no repeat of the Forza-avatar blue-screen.
- Added the CS chicken (real CC-BY poly.pizza model): wanders the area, one-shot kill.
- First-person ARMS/gloves gripping the AK (arms.kn5, built in the AK's exact local frame,
  driven with the identical transform; hidden for the knife).
- Weapon animation grounded in flashlight.lua (real values, cited by line): sway/idle/walk,
  camera-lag follow (:390 updateCameraResponse 0.15/3.0), recoil = CS-spec degrees; hand
  tremor dropped (rifle steadier than a light); + a procedural reload dip.
- HUD: CS radar (enemy blips, player arrow) + a 2D muzzle flash (replaced the debug-sphere).
- Movement: real crouch that lowers the eye 0.5 m (render-offset around the physics so it
  never fights the step/ground logic), on top of walk/jump/air-strafe.
- Attribution required on release: "Chicken by jeremy (poly.pizza), CC-BY 3.0". CS
  models/textures are Valve copyright - local/test use only.

#### Redone properly: native CS models + REAL CS animations (no shortcuts)
- The retargeting-to-CJ approach was wrong: it scrambled the in-engine textures and forced
  GTA (CJ) animations. Redone on the models' OWN native ValveBiped skeleton:
  `terrorist.kn5` + `ct.kn5` keep the SMD bind pose and UVs (no reposition), so the real
  decoded diffuse textures map exactly - texture garbling FIXED (validated by render).
- Animations are now REAL CS: `models/anims_cs/cs_idle.ksanim` (from the model's testIdle,
  rifle-carry stance) + `cs_walk.ksanim` (from testWalkN), converted SMD->ksanim v2 keyed to
  the ValveBiped bones. No more CJ/GTA clips.
- Death: the real CS death clip is in a shared t_animations.mdl that isn't present without CS
  installed - NOT faked. Placeholder = freeze a real CS idle pose + a procedural backward
  keel-over/sink (clearly a stand-in, not another game's animation). Real death pending CS install.
- All 3D debug primitives removed from the active render path (tracers/impacts/wireframe
  fallback); only failure-only fallbacks remain (never shown with the real models loaded).

#### Bots that fight back + spawn control + bot weapons
- Bot AI (`cfg.cs16_botAI`, default on): TR/CT bots detect the player within 55 m, chase
  (real CS walk anim) to 28 m, then hold and shoot with a line-of-sight raycast. Hits cost the
  player HP (armor absorbs half) with a red hurt-flash; at 0 HP the player resets in place.
- Spawn control: press **G** to spawn a bot exactly where you're aiming (camera raycast to
  ground/wall).
- Bots now hold a rifle: an AK is attached under each bot's `ValveBiped.Bip01_R_Hand` bone
  (child of the bone, follows the hand animation). Hand pose may need screenshot tuning.
- Honest note: this is bot AI I wrote (chase/aim/shoot), NOT a port of CS's engine AI (that
  isn't portable). Bot toggle + G control listed in the CS 1.6 tab.

#### Full CS animation set wired to bot state
- All 9 real CS `.ksanim` (71-bone ValveBiped, retargeted from the community CS/GMod
  animation source, no invented keyframes) are now deployed on both `terrorist.kn5` and
  `ct.kn5`: `cs_idle`, `cs_walk`, `cs_run`, `cs_fire`, `cs_death`, `cs_reload`,
  `cs_crouch_idle`, `cs_crouch_walk`, `cs_jump`.
- Bots now drive them from their AI state instead of a single frozen pose:
  chasing -> `cs_run` (phase from `walkPhase`), in-range-and-shooting -> `cs_fire` aim
  pose, otherwise -> `cs_idle`. The AI sets a new `e.attacking` flag (true only in the
  fire branch) that the render reads.
- Death now plays the REAL keyframed `cs_death` backward collapse (0 -> 0.85 of the clip
  over ~1 s, then holds - frames past 0.85 float where the source hands off to ragdoll,
  so we stop there). Replaces the old procedural keel-over.

#### Real CS:GO butterfly (balisong) knife viewmodel + real flip animation
- The knife viewmodel is no longer the procedural spinning placeholder. It is now the REAL
  Valve CS:GO `v_knife_butterfly` first-person viewmodel: the genuine decompiled Source1
  knife mesh (12k tris, the 4 balisong part-bones front/blade1/rear/lock) on its own
  `v_weapon.*` viewmodel skeleton, textured with the real Vanilla butterfly diffuse
  (VTF -> PNG, 2048²), exported to a skinned KN5 v6 (`models/weapons/butterfly.kn5`).
- Driven by the REAL decompiled CS:GO animations (converted to ksanim v2 on the same
  `v_weapon.*` skeleton, no invented keyframes): `draw`/`draw2` (deploy), `idle1`, and the
  signature `lookat01/02/03` balisong open/close FLIP, plus the `light_*`/`heavy_*` attacks.
  All in `models/weapons/v_knife_butterfly/`.
- New skinned-viewmodel path in `Vm` (cs16.lua): a state machine plays DEPLOY on (re)equip
  (random draw/draw2), then IDLE loop, with a periodic INSPECT flip (random lookat) whose
  swish sound is synced to the visual. The camera-relative root places+scales the whole rig;
  `setAnimation` poses the skeleton on top. `VM_TUNE['butterfly.kn5'].rot{}` aligns the
  authored viewmodel axes to the camera (screenshot-tunable).
- Verified offline before any in-game test: KN5 round-trip OK, the real texture maps
  correctly (no UV garble), and an FK+linear-blend-skinning render of a mid-`lookat01`
  frame shows the balisong cleanly split open (blade exposed, both handles rotated about
  the pivot) with no mesh tearing - proof the flip deforms correctly in-engine.
- Sourced from the community decompile `ilunp/CSGO-M.A.T` (real Valve assets; local
  reference/modding use). Pipeline tools in `scratchpad/butterfly_work/`.
- ARMS: added the real CS:GO first-person arms+gloves (BasildoomHD, GameBanana 171507,
  IDST v49) via a pure-Python Source1 MDL/VVD/VTX decompiler (`mdl_to_smd.py`, verified
  byte-exact vs the engine's poseToBone matrices), merged into `butterfly_hands.kn5` and
  driven by the same butterfly animations. `VM_FILE.knife` -> `butterfly_hands.kn5` (revert
  to knife-only `butterfly.kn5` in one line if the arms misbehave in-engine). Honest caveat:
  the community arms' per-vertex weighting doesn't perfectly match what Valve's butterfly
  animations expect, so the offline preview showed forearm artifacts - but that offline
  animated renderer (`render_anim.py`) is itself unreliable for this arm-bone hierarchy
  (rigid single-bone skinning, which cannot distort, still showed them), so the real check
  is in-engine. The static mesh is intact and the skinning pipeline is the same one the
  TR/CT bots use successfully.

#### Real per-weapon gun viewmodels (no more all-AK placeholder)
- USP-S, Glock-18, Desert Eagle, AK-47, M4A4 (M4A1 slot) and AWP now each have their REAL
  CS:GO Source1 viewmodel (decompiled SMD from `ilunp/CSGO-M.A.T`, real diffuse VTF->PNG),
  built to skinned KN5 and placed rigidly (the procedural sway/recoil animates them - guns
  don't need a skeleton). `VM_FILE` maps each weapon id to its own model; per-gun `VM_TUNE`
  (depth/scale/flipY). Batch pipeline: `scratchpad/butterfly_work/build_guns.py`.
- Orientation defaults to flipY=true (muzzle at local -Z, like the AK); depth/vertical are
  first-pass and may want a screenshot tweak per gun.

### New avatar: Forza Horizon 3 racing driver
- Ported the FH3 driver (helmet, visor, race suit, harness, gloves, boots) from the
  unencrypted dev build into `models/avatars/forza_driver.kn5`. Auto-discovered by the
  avatar picker (CUSTOM), no code change.
- Pipeline: extracted the driver mesh from `driver.modelbin` (full LOD0, filtered by
  name to include HeadGeo/helmet/visor/suit), rigged it to the CJ `DRIVER:DRIVER`
  skeleton via Blender Data Transfer weight painting (nearest-face), then exported KN5
  v6 skinned by TEMPLATE-SPLICE: kept CJ's 42-bone tree + every bone's inv_bind matrix
  byte-for-byte and swapped in only the Forza vertices/indices. This sidesteps the KN5
  writer's bind-matrix deform bug, so every `cj_*.ksanim` (walk/idle/run + emotes)
  drives it by bone name with zero retarget.
- Forza has NO extractable character animation (verified: driver.gr2 has 0 track groups
  across all 41 drivers; motion is procedural/IK in the exe) - which is why we inherit
  the mod's Mixamo->ksanim library instead.
- Validated by round-trip: re-imported the exported KN5 in Blender -> stands upright,
  complete, correct proportions. Texture is CJ's placeholder for now (the real suit
  texture is Oodle-packed in driver.gsf - a later refinement).

### Renamed the feature: "Showcase" -> "Homespace Cam" (it was mislabeled)
- The tab was wrongly associated with "ForzaVista". Verified against the FH3
  dev-build data: ForzaVista/Autovista is the INTERACTIVE walk-around-and-open-
  doors mode the player controls. What this feature actually ports is the
  AUTOMATIC, self-cutting menu cameras - in the engine they are cut-queues
  (`<Cams CutQueueType="Time">`, looping via `<Cam Type="ResetPlayback">`) that
  play on the "Homespace" (HomeSpaceCams.xml). The string "ForzaVista" appears in
  zero raw game files, so the old label was doubly wrong.
- Tab renamed `Showcase` -> `Homespace Cam`. Header now reads "AUTOMATIC HOMESPACE
  CAMERAS (auto cut-queue takes)". The "garage" scenario is renamed "Homespace"
  and its description names the real in-game moves (SLOW SPIN, SIDE DOLLY, PAN
  ACROSS, HELICOPTER). "Showcase" was also avoided because it collides with FH3's
  "Showcase Events" stunt races.
- Code: the main-file module alias `ForzaVistaModule` -> `HomespaceCam`. The
  module file stays `modulos/forzavista.lua` (private table unchanged) to keep the
  require path stable; a header comment documents the correct terminology. Saved
  settings keep their `fv_*` storage keys so nothing is wiped.

### Showcase cameras: nailed the Forza -> AC coordinate conversion
- Root cause of "cameras out of place / inside the car": the port mixed two
  coordinate frames. The camera POSITION went through the visual `bodyTransform`
  while the LOOK direction was built from the physics `car.side/look/up` vectors
  plus additive yaw/pitch. The two frames don't coincide, so the aim pointed back
  through the cabin and the shot framed the interior.
- Fix: everything now lives in ONE frame. Position AND look-at both route through
  `bodyTransform:transformPoint`, so they share the exact same basis. Removed the
  physics-vector look path (`carDirToWorld`) entirely.
- Nailed the axis remap (researched both engines, not guessed): both Forza car-space
  and AC car-local are left-handed, Y-up, +Z-forward, in metres, and differ ONLY in
  the sign of X (Forza +X = right, AC-local +X = left). So the conversion is
  `AC_local = (-x, y, z)` - negate X, keep Y, keep Z. The old "negate Z" idea (from
  AC *world* space) was wrong for `transformPoint` space and is gone. Negating X also
  mirrors the yaw/roll sense, which is now handled automatically because the look
  target is transformed the same way as the position.
- Vertical origin: no offset. Both frames put Y=0 on the ground plane, so Forza's
  absolute heights line up 1:1 - no more driver-eye/seat fudge.
- The global nudges (forward/back, left/right) now use the visual basis derived from
  `bodyTransform`, not the physics vectors, so they stay in the same frame as the rig.
- New "Origin shift (fwd/back)" slider for the rare car whose model root sits off the
  Forza pivot; defaults to 0 and persists. "Mirror fix" now defaults OFF (correct for
  standard AC models) and is only for mirrored mod models.

### Walkaround showcase camera + its own tab
- New `modulos/forzavista.lua` and a dedicated "Walkaround" tab in the main
  window. Press V next to a car to enter the showcase: A/D orbit, W/S step
  closer/farther, Ctrl crouch to inspect low details, hold Shift while still to
  focus in. Press V again to exit (the walking camera is handed back at the
  viewpoint so there is no jump).
- Not a plain orbit: it models the camera as a person's head. Blended eye height
  (standing 1.68 m / crouch 0.38 m), a standoff kept outside the car bounding box
  (proximity 1.15-3.35 m, 0.75 m inset), a crouch that flips the default pitch to
  look UP at the bodywork, a FOCUS state that cranes up and pulls in, and a subtle
  idle drift so the shot is never frozen.
- The key feel is the WEIGHT SHIFT: side-stepping leans the camera 3->20 deg,
  slides the head 0.3->0.8 m and adds yaw sway, with a fast lean-in and a slow
  wash-out - the "it's a person" tell a rigid orbit misses.
- Depth of field routes through the DOF module (track the car, blur the
  background) while active and restores your DOF settings on exit.
- All numbers are from the FH3 dev build (forza-camera-data/WalkaroundCamera.ini
  + Autovista.xml) and are exposed as sliders in the tab - no hidden preset.

### Phone Gyro: pairing lock + WiFi/USB choice + viewfinder capture methods
- Pairing handshake in the receiver: the phone app now challenges the receiver on
  connect and only streams once we answer with fnv1a(nonce + shared secret). This
  locks the app to our receivers (Walking Mod / Mobile Cam) so it can't be reused
  as a camera source elsewhere. Restart AC so the updated receiver loads.
- Connection transport WiFi/USB toggle in the Phone Gyro tab. WiFi = type the
  phone IP (as before). USB = one press: the mod runs `adb forward tcp:9876` and
  connects to 127.0.0.1 over the cable (no WiFi, no IP typing). reconnect=true
  covers the brief forward delay.
- Viewfinder capture method selector (NVENC / Software / Low) with a "restart
  viewfinder" button. NVENC shares the GPU encoder with OBS/ShadowPlay, so
  recording can lag the game; Software encodes on the CPU and frees NVENC so
  recording stays smooth; Low is NVENC at 30fps + lower bitrate for weak WiFi.
  The choice is passed to viewfinder-server.bat as an argument.

### Phone Gyro Track button: no forced roll + seamless release
- Pressing Track no longer banks the horizon. The tracker's automatic roll
  (pan-derived banking + idle handheld wobble) is suppressed while the phone is
  the camera, so tilting the phone owns roll and Track only changes where the
  camera aims. Manual Q/E roll still works; mouse/D-pad users are unchanged.
- Releasing Track now continues from exactly where the camera was left, then
  follows the phone. On unlock the phone's zero is re-anchored to the locked
  direction (base = lockedBase - current phone offset), so finalYaw stays at the
  locked direction with no snap and further phone motion carries on from there.
  Previously the base was set to the locked direction WITHOUT subtracting the
  phone offset, which snapped the view by the phone's current offset on release.

### Phone Gyro: 3DOF/6DOF split + car-entry config crash fix
- Car Entry no longer crashes with "attempt to compare number with string" in
  car_entry_runtime.lua update(). Root cause: the carEntry_* values were read back
  from ac.storage's generic string-key store, which returns RAW STRINGS (and "" for
  unset keys), so enterDurationSeconds and friends loaded as strings and blew up the
  numeric compare. The loader now coerces each value back to its default's type.
- 6DOF is now fully separate from 3DOF. The phone's rotation (aim) always drives the
  camera when Phone Gyro is on; the phone's physical POSITION (6DOF) is gated behind a
  new "Enable 6DOF" toggle in the Phone Gyro tab, OFF by default. So ARCore position
  drift can never move the camera unless you opt in -- aim keeps working regardless.

### Replay timeline (Director) + smoother motion blend
- New REPLAY TIMELINE in the Recorder tab: a scrub bar bound to the game replay
  (reads replayCurrentFrame/replayFrames, seeks with ac.setReplayPosition) with a live
  frame/percent preview. Foundation for the Rockstar-Editor-style camera director.
- Recorder "Sync with replay" toggle: when on, Start Recording waits until the replay is
  actually playing, then records in lock-step with the replay timeline (frames line up
  with the replay) instead of wall-clock time. Self-persists. Off = old real-time behavior.
  PLAYBACK of a synced template now also follows the replay (waits for it to play, samples
  by replay frame, holds at the ends so you can scrub) -- before, a synced template played
  by wall-clock and did nothing because its timestamps were in replay frames, not seconds.
- Recorder PLAYBACK now drives the camera DURING a replay even when you are not on foot.
  The playback used to live only inside the on-foot update, so watching a replay from the
  car / free cam ran nothing ("play does nothing"). It now grabs the camera and applies the
  recorded pose every frame (ownShare held, like the dolly), and releases it when done.
- Smoother motion->procedural transition when stopping from a run. The procedural shake
  was a BINARY zero while the Blender motion was enabled, so it snapped back to full the
  instant the motion ended (the felt switch). Now motion and procedurals CROSSFADE by the
  motion blend (motion * blend, procedurals * (1 - blend)) -- one smooth line.
- Run transition no longer has a visible "you can see exactly where it starts and ends"
  kick. The motion blend was applied LINEARLY (velocity jump at the 0/1 corners) and the
  run's position bob entered at full amplitude with no blend at all. Both are now eased
  (smoothstep): the bob fades in/out and the rotation crossfade has zero velocity at both
  ends, so the run eases in and out as one continuous motion.
- KEYFRAME DIRECTOR: place camera keyframes on the replay timeline (park the camera where
  you want a shot -- scrubbed or paused -- and "Add keyframe"), then play and the camera
  tracks in a STRAIGHT LINE between them in step with the replay. You set point A at one
  replay moment and point B at a later one (e.g. where a fast car will be) and the camera
  follows A->B as the replay rolls. Keyframe ticks + their frame numbers shown on the bar.
- Switched the path from a Catmull-Rom CURVE to a straight line: the curve could swing wide
  of the two points and overshoot, which read as the camera teleporting. Straight A->B just
  tracks point to point. Also warns in the UI when two keyframes sit on nearly the same
  replay frame (the move would be near-instant -- space them out in time).
- Director TELEPORT fixed (it used to jump instead of slide). Root causes, all addressed:
  (1) authoring while PAUSED collapsed every pose onto the same frozen replay frame via the
  "replace within 2 frames" rule, leaving a single keyframe -- now distinct paused poses
  stack into consecutive free frames and only a true re-aim (same frame AND ~same position)
  replaces; (2) a zero/short span fell back to t=1 and snapped to the next keyframe -- now
  holds (t=0); (3) the segment search defaulted to keyframes 1-2 on a miss -- now the last
  segment; (4) look vectors are normalized at capture and on interpolation so opposite-facing
  shots no longer pass through a degenerate direction; (5) pressing play SNAPPED from the
  free cam to the first keyframe -- now it ENGAGE-EASES (smoothstep, ~0.6s) from wherever the
  camera is into the path, so it works paused too (press play and it glides to the shot).
- "Rewind & play director" button: the director follows the replay clock, so this jumps the
  replay to the start and arms the director so the shot rolls from the beginning (before, if
  you played from past the last keyframe it just held the last pose and looked static).
- Per-keyframe ZOOM: "Add keyframe" captures the free-cam FOV (pcall-guarded, no unverified
  sim field) so each shot can have its own zoom, eased with smoothstep between keyframes.
- Recorder auto-links to the replay: starting a recording while a replay is open now records
  in lock-step with the replay timeline automatically (no need to remember the "Sync with
  replay" toggle). Each captured frame is tagged with its replay moment.
- Re-record a SECTION of a take: "Re-record from here" button. Scrub the replay to where the
  shot went wrong, click it, and play the replay -- the new camera overwrites the take from
  that point as the replay rolls. Everything before it, and after you stop, is kept. Lets you
  fix the spot where you lost a fast car without redoing the whole take.
- Scene SMOOTHNESS slider: low-passes the applied camera on playback so the recorded scene
  is gentler and more subtle (filters the hand jitter baked into the take). Frame-rate-aware
  exponential smoothing; higher = smoother with a touch more lag. Applies to recorder
  playback and the director. Self-persists; defaults to a moderate amount.

### Camera feel, avatar and UI fixes
- Run-on-the-spot no longer shakes the camera: the run head-bob AND the Blender run
  motion now require actual movement (gated on movement intensity), so holding the run
  key while standing still is steady.
- More momentum on start/stop, especially stopping from a run (softer accel/decel +
  higher run-stop inertia). Pushed to existing saved configs via a one-time migration.
- Avatar no longer sinks into the ground: the foot-plant was pinning the ankle bone to
  the ground (sole below it). footPlantBias now lifts it so the sole rests on the ground.
- Avatar in replay is opt-in: turning on a replay no longer auto-shows the avatar
  (Hide in Replay now defaults on).
- Master "Avatar: ON / OFF" button in the header (always visible) turns the on-foot 3D
  character off everywhere (you, other players, replay, test) for people who don't want one.
- Avatar toggles now PERSIST across reloads (ac.storage): the master Avatar ON/OFF and the
  avatar tab toggles (sync, test, remote, in-car, third-person, hide-in-replay, sync-status)
  are remembered. Turning the avatar off keeps it off after a restart -- before it reset on.
- Sync status readout hidden by default (debug clutter), with a checkbox to re-enable it.
- Version number shown clearly in the header (was a faint gray).
- Removed the camera roll/lean when running (the lateral bank added earlier) -- it never
  shipped and was not wanted.

Groundwork for the car enter/exit feature: a continuous first-person camera that
flows from standing into the cockpit (handed over to Neck FX with no cut), plus the
avatar opening the door and sitting down.

### Car Entry (work in progress)
- New "Car Entry" settings tab with explicit, didactic controls for the upcoming smooth
  enter/exit: enable toggle, enter/exit duration, door choreography (open/sit/close timing
  and door angle), camera blend window, the Neck FX blend cap (measured 0.84, kept under
  the 0.85 cameraRestoreThreshold so Neck FX stays live during the blend), and a per-car
  driver-eye offset (defaults to the ks_mazda_miata DRIVEREYES). Off by default; values
  persist via ac.storage.
- Wired the motion (still gated off): a new modulos/car_entry_runtime.lua drives, during
  enter/exit, the door (scrubs the car's own car_door_L.ksanim 0..65 deg), the avatar body
  (plays models/car/cj_enter_car.ksanim), and a seamless camera blend from the standing eye to
  the driver eye (grabbed-camera ownShare capped under the measured 0.85 so Neck FX stays live).
  All five hooks are additive and guarded by WalkingCam.carEntry.enabled, so with the toggle off
  the existing behavior is byte-for-byte unchanged. Needs in-engine tuning via the tab sliders.

### Internal / modularization
- Moved the 14 pre-allocated UI colors from main-chunk locals onto the global
  `WalkingCam` table. The main file was at 201 top-level locals, right at Lua's
  200-per-chunk ceiling; this frees 14 slots (now 187) so the new car-entry state
  machine has room without tripping "more than 200 local variables". No behaviour
  change, the colors render the same.

## [2.1.0] - 2026-05-31

Big pass on the avatar system, replay, tracking and settings. The "boneco"
(the on-foot 3D character) is now consistently called the **Avatar** across the
whole codebase and UI.

### Tracking
- Removed the AI track-spline aim entirely. On drift tracks (Ebisu, Akina, etc.)
  the AI spline returned NaN coordinates; because `NaN * 0 = NaN`, that NaN leaked
  into the aim point even when the spline blend was 0, killed the aim, and dropped
  the camera back to free-look. This was the "tracking keeps losing the car" bug.
  Aim is now predict-only.
- `focusedCar == -1` (replay free/heli/track cameras) no longer kills tracking;
  it falls back to car 0.
- When the tracked car briefly returns nil (pit, respawn, replay despawn) the aim
  now holds the last known target for a short grace window instead of snapping to
  free-look.
- Added a hard timeout so the frame-rate sync can never freeze the aim on a stale
  car position.
- Diagnostics (good/nil frame counters, per-cause breakdown) moved out of the top
  of the Tracking tab into a collapsed "Diagnostics" node at the bottom.

### Tracking roll
- Fixed the camera roll drifting on its own. Manual roll input was being read in
  two places per frame; the second reader overwrote the first with 0, so Q/E never
  worked and a bound/drifting pad axis could push roll by itself. Unified into one
  reader (Q/E + rebindable keys + reset, clamped).
- Added an "Auto-roll / banking" master toggle. Off keeps the horizon level on its
  own (no dynamic banking, no idle wobble); manual Q/E roll still works.

### Avatar (renamed from "Stickman")
- Renamed the whole concept to Avatar: `StickmanConfig` to `AvatarViewConfig`,
  `StickmanAdvanced`/`StickmanModule` to `AvatarRenderer`, `StickmanAnimState` to
  `AvatarAnimState`, `drawStickman` to `drawAvatar`, the `showTestStickman` field
  to `showTestAvatar`, and the module file `modulos/stickman_advanced.lua` to
  `modulos/avatar_advanced.lua`. Saved-preset keys kept their old `stickman_`
  names for backward compatibility.
- Tabs renamed: "Stickman" to "Avatar", "Character" to "Avatar Model", "Driver"
  to "Walk Mode".

### Avatar picker
- Real dedupe by KN5 file identity: "CJ", "CJ (Driver)" and "Lm carlgtasa" now
  collapse into a single entry (priority Mod > Custom > Driver).
- Grouped by source: MOD / CUSTOM (models/avatars) / DRIVER (content/driver), with
  the long driver list collapsible and a search box.
- Friendly auto-names: dropping `red_ferrari_guy.kn5` into models/avatars shows
  "Red Ferrari Guy" with no code edits.
- Removed the redundant "Quick Select" combo that never listed drivers.
- Ships with only CJ as a built-in avatar; everything else is discovered from the
  player's own folders (models/avatars and content/driver). The previously bundled
  extras (Cheems, Mixamo, Ch44, Roblox) were moved to models/avatars/_unused.
- Selected avatar is now saved by a stable key instead of a list index, so it
  survives the picker re-sorting.
- Fixed the avatar floating and the orbital preview cutting off half the body: the
  preview was using the eye position as the ground, so the avatar sat ~1.7m too
  high and the camera aimed above the head. It now derives the real feet position.

### Replay
- The recorded walk now plays back on the avatar in replays. Recording used to be
  tied to the third-person draw, so walking in first person recorded nothing and
  the avatar stood still in the replay. Recording is now decoupled and runs every
  frame while on foot, in any view.
- Entering a replay no longer leaves a frozen live avatar with the camera orbiting
  it. The live walking camera is released to AC's native replay cameras and the
  live body is hidden; only the recorded avatar plays.
- "Hide in Replay" now means "no avatar in replay at all" (default off, so the
  recorded walk shows).

### Settings
- Fixed settings resetting / loading differently on some starts. Settings only
  loaded on the first car exit, so a slider or keybind touched before that wrote
  the defaults back over the saved config. Settings now load on the first frame,
  and saving is blocked until the first load has happened.
- Added a Lua syntax + 200-local-limit check to the dev workflow so reloads do not
  hit the "main function has more than 200 local variables" error.

### Keybinds & hold
- Hold-to-activate is now ON by default for every keybind, with a per-key opt-out.
  Previously a key only entered hold mode if a saved value existed, so on a fresh
  config the hold branch never ran and toggles fired on the press edge — the
  "hold clica de imediato" bug. Hold now requires holding the key for 1 second
  before it activates, matching the Mobile Cam feel.
- Removed the Race Start / Race Referee keybind. The Race Referee feature isn't
  implemented yet, so the bind and its Keybinds-tab entry were removed.

### UI
- Passenger mode is hidden for now (parked feature).
- The Avatar tab's sync status ("Initializing…", Sent/Recv/Players packet counts)
  moved from the top of the tab to the bottom, under a "SYNC STATUS" heading, so
  it no longer clutters the controls.

### Avatar (more)
- Ships with only CJ as a built-in avatar; the previously bundled Cheems, Mixamo,
  Ch44 and Roblox were moved to models/avatars/_unused. Everything else comes from
  the player's own folders.
- Fixed the avatar staying frozen on screen after being picked in first person.
  Nothing hid the local avatar when returning to first person; it now hides each
  frame when not in third person and not in the picker preview.

### Presets
- Fixed MyPreset and MyPreset alt: removed dead AI-spline/aim-assist keys (features
  gone), added the new trackingAutoRoll and avatar_selectedKey keys, and de-duped.
- Added two ready-made presets: "Stable Camera" (smooth/cinematic, stable horizon)
  and "Unstable Camera" (handheld/documentary), both with realistic smooth scroll
  zoom.

### Replay
- Fixed not being able to exit the car / walk during a replay. A guard added
  earlier made walking mode bail out whenever a replay was active, which also
  blocked exiting the car to film on foot. It now only releases the camera to the
  native replay cam when you are still in the car (just watching); once you exit
  on foot, walking and the camera work normally during replay.

### Animations / foot-plant
- Added a foot-plant pass so the avatar's feet sit on the ground instead of
  floating. After each frame's pose, it reads the foot bone's real world position
  (SceneReference:getWorldTransformationRaw) and pushes the model down so the foot
  rests on the ground. The bone we can read is the ankle, which sits above the
  actual sole, so there's a tunable AvatarConfig.footPlantBias to line the sole
  up exactly (the CJ idle and dance animations were authored ~45cm apart in foot
  height, which is why the dances looked grounded and the idle floated). Toggle
  with AvatarConfig.footPlantEnabled. Idle ksanim root edits from the earlier
  attempt are reversible via *.ksanim.bak_footplant.

### Movement
- Fixed the avatar sliding horizontally across the ground ("ice" / foot-skating)
  while standing still. When you released the movement keys, velocity blended
  toward zero exponentially but never actually reached it, and updatePosition
  kept integrating that tiny leftover velocity every frame, so the body glided
  forever. Added a residual-speed floor in movement.lua: while there's no input,
  velocity snaps to exactly zero once it drops below minResidualSpeed (0.02 m/s).
  This also finally wires up the minResidualSpeed config/slider, which was defined
  but never read.

### Emotes
- Added a Thriller dance emote, retargeted onto CJ through the Blender pipeline
  (Mixamo skeleton to the CJ rig, foot-planted, exported as ksanim). Plays at 1:1
  speed (566 frames at 30fps, ~19s).
- Added a Macarena emote (Mixamo-rigged source) and an Orange Justice emote (Fortnite),
  both retargeted onto CJ, foot-planted and played in place.
- Added a Criss Cross emote (Fortnite floor dance), retargeted onto CJ.
- Added Electro Swing and Crackdown emotes (Fortnite), retargeted onto CJ.

### Credits
- Thriller emote motion is based on "Thriller Dance By Michael Jackson" by Ace-Jane
  on Sketchfab, used under Creative Commons Attribution 4.0 (CC-BY).
  https://sketchfab.com/3d-models/thriller-dance-by-michael-jackson-2ad90c9406cc44cf9cecef6ad79fda98
- Macarena emote motion is based on "Skeleton- Macarena Dance" by yigitayyildiz on
  Sketchfab, used under Creative Commons Attribution 4.0 (CC-BY).
  https://sketchfab.com/3d-models/skeleton-macarena-dance-a3e77bfcdc014264baba69a5951d324b
- Orange Justice emote motion is based on "Orange justice" by Coldary on Sketchfab,
  used under Creative Commons Attribution 4.0 (CC-BY).
  https://sketchfab.com/3d-models/orange-justice-31b3596641af4e238c1491c450cc6df5
- Criss Cross emote motion is based on "Fortnite Splatterella With Criss Cross Emote" by
  AstroNatee on Sketchfab, used under Creative Commons Attribution 4.0 (CC-BY).
  https://sketchfab.com/3d-models/fortnite-splatterella-with-criss-cross-emote-b71030dca31d450f9d1a924050805fce
- Electro Swing and Crackdown emote motions are based on "Electroswing" and "Crackdown emote
  Fortnite" by Coldary on Sketchfab, used under Creative Commons Attribution 4.0 (CC-BY).
  https://sketchfab.com/3d-models/electroswing-b16232a3f1a443248f964492ab1dc151
  https://sketchfab.com/3d-models/crackdown-emote-fortnite-1731fea303914d7eb82531fcec44f4fb

### Aimbot
- Added a single "Completely Stable (no sway)" checkbox at the top of the Aimbot tab.
  On keeps the aim perfectly locked with no sway or drift; off leaves it as it is,
  with the natural human-like movement. It drives the Natural Tracking and Stabilized
  Lock options together so you do not have to set both by hand.
- The camera Motion layer complements the aimbot: with a motion running, even a locked
  aim still breathes with a subtle handheld feel, so the whole shot looks more realistic.

### Motion
- Fixed the Motion list sometimes not loading. The loader listed the motions folder with
  a shell dir command that intermittently fails in AC's sandbox; it now uses CSP's native
  directory scan first, with the old method and a known-files list as fallbacks.

### Keybinds & hold (fix)
- Hold-to-activate now actually applies to the emote and dance keys. They were read on the
  raw press edge and fired instantly, ignoring the hold setting. Hold time is 1 second.

### Misc
- Renamed the "CineMotion" labels in the UI to "Motion".
