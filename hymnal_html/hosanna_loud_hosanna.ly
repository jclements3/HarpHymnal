\version "2.22.1"

\header {
  title = "100  Hosanna, Loud Hosanna"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key bes \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf bes'4 a'8 g'8 f'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 ees'4 \acciaccatura { g'16 ees'16 } f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 a'8 bes'4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { ees''16 c''16 } d''2. | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 a'8 g'8 f'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 ees'4 \acciaccatura { g'16 ees'16 } f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 a'8 bes'4 bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'2. | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''8 d''4 c''4 d''4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''4 a'8 bes'8 c''4 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''8 d''4 c''4 \acciaccatura { ees''16 c''16 } d''4 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''2. | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } bes'4 a'8 g'8 f'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'4 ees'4 \acciaccatura { g'16 ees'16 } f'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } g'8 a'8 bes'4 bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { c''16 a'16 } bes'2. | }
    { \voiceTwo <bes d'>1\p\arpeggio | g'1 | <bes d'>1\arpeggio | <bes d' f'>1\arpeggio | <bes d'>1\arpeggio | g'1 | <bes d'>1\arpeggio | <bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | <ees' f'>1\arpeggio | <bes d' f'>1\arpeggio | <ees' f' a'>1\arpeggio | <ees f a c'>1\arpeggio | g'1 | <a c' ees'>1\arpeggio | <a c' ees' f'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <f a c'>1\p\arpeggio | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 f4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 g4 | \acciaccatura { f,8 } <f a bes d'>4\arpeggio a8 bes8 d'8 a8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 f4 | \acciaccatura { f,8 } <f a bes d'>4\arpeggio a8 bes8 d'8 a8 g4 | \acciaccatura { f,8 } <f a bes d'>4\arpeggio a8 bes8 d'8 a8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f g>4\arpeggio d8 f8 g8 d8 c4 | \acciaccatura { bes,,8 } <bes, d f g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
