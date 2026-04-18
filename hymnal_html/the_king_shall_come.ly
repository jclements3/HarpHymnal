\version "2.22.1"

\header {
  title = "247  The King Shall Come"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf f'4 g'4 aes'4 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'8 g'4 f'8 ees'8 \acciaccatura { des'16 bes16 } c'4 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } f'4 g'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } c''2. | aes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'8 c''4 des''8 c''8 bes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 f'8 ees'8 \acciaccatura { des'16 bes16 } c'4 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } f'4 g'4 aes'8 f'8 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { g'16 ees'16 } f'2. | }
    { \voiceTwo <bes des'>1\p\arpeggio | aes1 | ees'1 | <ees' g'>1\arpeggio | g'1 | des'1 | <bes ees'>1\arpeggio | <bes ees'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <aes, c ees>1\p\arpeggio | \acciaccatura { bes,,8 } <g, bes, des>4\arpeggio bes,8 des8 bes,8 des8 g,4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c des>4\arpeggio aes,8 c8 des8 aes,8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 c4 | \acciaccatura { bes,,8 } <g, bes, des>4\arpeggio bes,8 des8 bes,8 des8 g,4 | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 g4 | \acciaccatura { f,8 } <des f aes>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
