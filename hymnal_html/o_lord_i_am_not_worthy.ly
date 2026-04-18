\version "2.22.1"

\header {
  title = "193  O Lord, I Am Not Worthy"
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
    { \voiceOne d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf ees'8 f'4 g'4 f'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 a'2 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'8 c''4 ees'4 g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } \acciaccatura { ees'16 c'16 } d'2. | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } ees'8 f'4 f'4 bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } } } a'4 g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 bes'4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { c''16 a'16 } bes'2. | }
    { \voiceTwo <a c'>1\p\arpeggio | <bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | <d f a>1\arpeggio | a'1 | <c' d' f'>1\arpeggio | ees'1 | <a c' ees' f'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <bes, d f g>1\p\arpeggio | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 g4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 ees4 | \acciaccatura { d,8 } <d ees g bes>4\arpeggio ees8 g8 bes8 ees8 f4 | \acciaccatura { ees,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
