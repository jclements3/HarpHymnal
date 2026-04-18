\version "2.22.1"

\header {
  title = "007  Abide With Me"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key ees \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf g'4 f'4 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 bes'4 \acciaccatura { bes'16 g'16 } aes'4 | g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'4 bes'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } \acciaccatura { c''16 aes'16 } bes'2 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } f'4 g'4 a'4 | bes'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 \acciaccatura { g'16 ees'16 } f'4 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } bes'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'4 aes'4 g'4 | f'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } | f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } g'4 \acciaccatura { bes'16 g'16 } aes'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 ees'4 aes'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'2 | \acciaccatura { f'16 d'16 } ees'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <ees g bes>1\p\arpeggio | <c' g'>1\arpeggio | <ees' g'>1\arpeggio | <aes c' ees'>1\arpeggio | <aes c' ees'>1\arpeggio | <aes c' ees'>1\arpeggio | <bes d'>1\arpeggio | <ees' g'>1\arpeggio | <ees g bes>1\arpeggio | <c' g'>1\arpeggio | <aes c' ees'>1\arpeggio | <bes d'>1\arpeggio | <bes c' ees'>1\arpeggio | <ees g bes>1\arpeggio | <d f aes bes>1\arpeggio | <aes c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <c ees g>1\p\arpeggio | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 f,4 | \acciaccatura { f,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 f,4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 c4 | \acciaccatura { c,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 g,4 | \acciaccatura { f,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 c4 | \acciaccatura { bes,,8 } <bes, d f aes>4\arpeggio d8 f8 aes8 d8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 f,4 | \acciaccatura { ees,8 } <ees, g, bes, c>4\arpeggio g,8 bes,8 c8 g,8 f,4 | \acciaccatura { ees,8 } <ees, g, bes,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
