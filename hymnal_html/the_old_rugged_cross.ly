\version "2.22.1"

\header {
  title = "254  The Old Rugged Cross"
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
    { \voiceOne d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf ees'8 f'4. e'8 g'4 f'2 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } f'8 g'4. fis'8 a'4 \acciaccatura { a'16 f'16 } g'2 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 a'4. g'8 f'4 ees'4 f'4 | ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d'2. d'2 | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees'8 f'4. e'8 g'4 f'2 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } f'8 g'4. fis'8 a'4 \acciaccatura { a'16 f'16 } g'2 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 a'4. g'8 f'4 ees''4 d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'2. \acciaccatura { c''16 a'16 } bes'2 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'8 c''4. c''8 c''4 c''4 bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } bes'2. bes'2 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'8 g'4. g'8 g'4 bes'4 \acciaccatura { bes'16 g'16 } a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'2. f'2 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'8 d''4. d''8 d''4 d''4 ees''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'2. g'2 | ees''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } ees''8 d''4. c''8 bes'4 f'4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes'2. \acciaccatura { c''16 a'16 } bes'2 | }
    { \voiceTwo <ees g bes>1.\p\arpeggio | <ees g bes>1.\arpeggio | c'1. | <ees g bes>1.\arpeggio | <ees g bes>1.\arpeggio | <f a c'>1.\arpeggio | <bes d'>1.\arpeggio | <bes d' f'>1.\arpeggio | <bes d' f'>1.\arpeggio | <a bes d' f'>1.\arpeggio | ees'1. | <ees g bes>1.\arpeggio | <ees' g'>1.\arpeggio | <ees' bes'>1.\arpeggio | <a c' ees'>1.\arpeggio | <a c' ees' f'>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <bes, d f>1.\p\arpeggio | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 ees8 g8 ees8 g8 c4 | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 f4 | \acciaccatura { ees,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 ees4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 a8 c'8 a8 c'8 f4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 ees8 g8 d8 ees8 f4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 f4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f g>4\arpeggio d8 f8 g8 d8 f8 g8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f g>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
