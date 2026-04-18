\version "2.22.1"

\header {
  title = "044  Breathe on Me, Breath of God"
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
    { \voiceOne f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf c''4 bes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 f'2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } ees''4 des''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 c''2 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 \acciaccatura { g'16 ees'16 } f'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } aes'4 bes'4 aes'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } f'4 c''4 \acciaccatura { c''16 aes'16 } bes'4 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'2 | \acciaccatura { g'16 ees'16 } f'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo <bes ees' g'>1\p\arpeggio | <f aes c'>1\arpeggio | <ees' g' bes'>1\arpeggio | <f' aes'>1\arpeggio | des'1 | <des' f'>1\arpeggio | <bes ees'>1\arpeggio | <bes ees'>1\arpeggio | <bes, ees g>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <des f aes>1\p\arpeggio | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 bes,4 | \acciaccatura { aes,,8 } <f, aes, c des>4\arpeggio aes,8 c8 des8 aes,8 bes,4 | \acciaccatura { aes,,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 g4 | \acciaccatura { f,8 } <g, bes, des>4\arpeggio bes,8 des8 bes,8 des8 g,4 | \acciaccatura { bes,,8 } <g, bes, des>4\arpeggio bes,8 des8 bes,8 des8 g,4 | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 des4 | \acciaccatura { f,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 g4 | \acciaccatura { f,8 } <des f aes>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
