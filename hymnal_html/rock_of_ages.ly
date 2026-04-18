\version "2.22.1"

\header {
  title = "220  Rock of Ages"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key bes \major
  \time 6/4
}

upper = {
  \global
  <<
    { \voiceOne f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf g'8 f'2 d'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'8 f'1 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''8 d''2. c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 \acciaccatura { c''16 a'16 } bes'1 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'8 c''2. c''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 \acciaccatura { c''16 a'16 } bes'1 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'8 c''2. c''4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } f'4 \acciaccatura { c''16 a'16 } bes'1 | f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } g'8 f'2 d'2 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "6" } } } g'8 f'1 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''8 d''2. c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 \acciaccatura { c''16 a'16 } bes'1 | }
    { \voiceTwo <a c' ees'>1.\p\arpeggio | <a c' ees'>1.\arpeggio | <ees' g'>1.\arpeggio | <bes d' f'>1.\arpeggio | <bes d' f'>1.\arpeggio | <bes d'>1.\arpeggio | <bes d' f'>1.\arpeggio | d'1. | <d f a bes>1.\arpeggio | <d' a'>1.\arpeggio | <ees' g'>1.\arpeggio | <ees' g'>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <bes, d f g>1.\p\arpeggio | \acciaccatura { bes,,8 } <bes, d f g>4\arpeggio d8 f8 g8 d8 f8 g8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 a8 c'8 a8 c'8 f4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 a8 c'8 a8 c'8 f4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <ees g bes c'>4\arpeggio g8 bes8 c'8 g8 bes8 c'8 g8 bes8 ees4 | \acciaccatura { bes,,8 } <ees g bes c'>4\arpeggio g8 bes8 c'8 g8 bes8 c'8 g8 bes8 c4 | \acciaccatura { bes,,8 } <ees g bes c'>4\arpeggio g8 bes8 c'8 g8 bes8 c'8 g8 bes8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
