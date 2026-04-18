\version "2.22.1"

\header {
  title = "162  More Love to Thee"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key aes \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf f'4 ees'4 | aes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'8 \acciaccatura { des''16 bes'16 } c''2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 aes'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } | ees'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'4 \acciaccatura { f'16 des'16 } ees'4 | aes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'8 c''2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } aes'4 g'4 | \acciaccatura { bes'16 g'16 } aes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } | des''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } des''4 des''4 | des''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''8 c''2 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } bes'4 \acciaccatura { c''16 aes'16 } bes'4 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } aes'8 aes'2 | f'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 f'4 | aes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } aes'4 g'4 | \acciaccatura { bes'16 g'16 } aes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <g bes des'>1\p\arpeggio | <des' f'>1\arpeggio | <aes c' ees'>1\arpeggio | <des' ees' g'>1\arpeggio | <g bes des'>1\arpeggio | <bes des' f'>1\arpeggio | <bes des' f'>1\arpeggio | <g aes c' ees'>1\arpeggio | <ees' g' bes'>1\arpeggio | <ees' g' bes'>1\arpeggio | <ees f aes c'>1\arpeggio | <ees' g'>1\arpeggio | <des f aes>1\arpeggio | <aes c' ees'>1\arpeggio | <des' ees'>1\arpeggio | <des' f'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { aes,,8 } <aes, c ees f>1\p\arpeggio | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 aes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees f>4\arpeggio c8 ees8 f8 c8 aes,4 | \acciaccatura { aes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 c4 | \acciaccatura { bes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <aes, c des f>4\arpeggio c8 des8 f8 c8 aes,4 | \acciaccatura { des,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 ees4 | \acciaccatura { des,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 f4 | \acciaccatura { ees,8 } <ees g bes des'>4\arpeggio g8 bes8 des'8 g8 ees4 | \acciaccatura { ees,8 } <des f aes>4\arpeggio f8 aes8 f8 aes8 ees4 | \acciaccatura { des,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 bes,4 | \acciaccatura { aes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees g aes c'>4\arpeggio g8 aes8 c'8 g8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
