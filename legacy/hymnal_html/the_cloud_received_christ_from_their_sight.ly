\version "2.22.1"

\header {
  title = "240  The Cloud Received Christ From Their Sight"
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
    { \voiceOne ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf aes'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { c''16 aes'16 } bes'2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } aes'2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { ees''16 c''16 } des''2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'1 | r1. | ees''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } ees''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { des''16 bes'16 } c''2 | aes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'2 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 ees'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { bes'16 g'16 } aes'2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'1 | r1. | }
    { \voiceTwo <aes c'>1.\p\arpeggio | <aes c' ees'>1.\arpeggio | <c' f' aes'>1.\arpeggio | <ees f aes c'>1.\arpeggio | <des' ees' g'>1.\arpeggio | <aes c' ees'>1.\arpeggio | <aes c' ees'>1.\arpeggio | <des'' ees'' g'' bes''>1.\arpeggio | <des' ees' g' bes'>1.\arpeggio | <g bes des' ees'>1.\arpeggio | <des' f'>1.\arpeggio | <des f aes>1.\arpeggio | des'1. | <aes c' ees'>1.\arpeggio | <des' ees' g'>1.\arpeggio | <des'' f'' aes''>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <ees g bes>1.\p\arpeggio | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 ees4 | \acciaccatura { ees,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g bes des'>4\arpeggio g8 bes8 des'8 g8 bes8 des'8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 aes8 c'8 g8 aes8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 ees4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 aes8 c'8 g8 aes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 aes8 c'8 g8 aes8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees f>4\arpeggio c8 ees8 f8 c8 ees8 f8 c8 ees8 aes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 ees4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 ees4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 ees4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 aes8 c'8 g8 aes8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
