\version "2.22.1"

\header {
  title = "018  All Who Believe and Are Baptized"
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
    { \voiceOne bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf bes'4 bes'4 bes'4 cis''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 \acciaccatura { bes'16 g'16 } aes'4. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 ees'4 g'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 bes'4. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 bes'4 bes'4 \acciaccatura { ees''16 b'16 } cis''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 aes'4. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 ees'4 g'4 aes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 bes'4. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } ees''4. cis''8 c''4 \acciaccatura { c''16 aes'16 } bes'4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 bes'4. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } ees''4. bes'8 bes'4 \acciaccatura { f'16 d'16 } ees'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } bes'4 g'4. | ees'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } f'4 aes'4 g'4 f'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } f'4 \acciaccatura { f'16 d'16 } ees'4. | }
    { \voiceTwo <ees' g'>1\p\arpeggio | <ees' g'>1\arpeggio | r1 | <ees' g'>1\arpeggio | <ees' g'>1\arpeggio | <ees' g'>1\arpeggio | r1 | <ees' g'>1\arpeggio | <ees' g'>1\arpeggio | <ees' g'>1\arpeggio | <bes d' f'>1\arpeggio | <g bes d' ees'>1\arpeggio | <g bes d'>1\arpeggio | <g bes d'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <bes, d f>1\p\arpeggio | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 d4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 f4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 f,4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 d4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 f4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <aes, c ees>4\arpeggio c8 ees8 c8 ees8 aes,4 | \acciaccatura { aes,,8 } <aes, c ees f>4\arpeggio c8 ees8 f8 c8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees f>4\arpeggio c8 ees8 f8 c8 bes,4 | \acciaccatura { aes,,8 } <aes, c ees f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
