\version "2.22.1"

\header {
  title = "197  O That The Lord Would Guide My Ways"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key aes \major
  \time 3/2
}

upper = {
  \global
  <<
    { \voiceOne ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf ees'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } aes'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } \acciaccatura { f'16 des'16 } ees'2 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } ees'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''2 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'1 | r1. | des''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { g'16 ees'16 } f'2 | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } ees'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'1 | r1. | }
    { \voiceTwo <aes c'>1.\p\arpeggio | <aes c' ees'>1.\arpeggio | <ees' g'>1.\arpeggio | <des f aes>1.\arpeggio | <aes c'>1.\arpeggio | <aes c' ees'>1.\arpeggio | <f aes c'>1.\arpeggio | <c'' f'' aes''>1.\arpeggio | <ees' f' aes'>1.\arpeggio | <des' ees' g'>1.\arpeggio | <des' ees' g'>1.\arpeggio | <aes c' ees'>1.\arpeggio | <f aes c'>1.\arpeggio | f'1. | <des' ees' g'>1.\arpeggio | <des'' f'' aes''>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { aes,,8 } <ees g bes>1.\p\arpeggio | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 f8 aes8 f8 aes8 ees4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 aes,4 | \acciaccatura { aes,,8 } <f aes c'>4\arpeggio aes8 c'8 aes8 c'8 aes8 c'8 aes8 c'8 bes4 | \acciaccatura { aes,,8 } <f aes c'>4\arpeggio aes8 c'8 aes8 c'8 aes8 c'8 aes8 c'8 g4 | \acciaccatura { f,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 ees4 | \acciaccatura { ees,8 } <ees g bes des'>4\arpeggio g8 bes8 des'8 g8 bes8 des'8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 aes8 c'8 g8 aes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 aes8 c'8 g8 aes8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 ees4 | \acciaccatura { ees,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 g4 | \acciaccatura { f,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 aes8 c'8 g8 aes8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
