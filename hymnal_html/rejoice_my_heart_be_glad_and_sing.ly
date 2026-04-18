\version "2.22.1"

\header {
  title = "218  Rejoice, My Heart, Be Glad and Sing"
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
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf f'4 f'4 f'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 a'4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 a'4 \acciaccatura { a'16 f'16 } g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } f'2. | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } bes'4 c''4 d''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } ees''4 d''4 \acciaccatura { d''16 bes'16 } c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 d''4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } \acciaccatura { c''16 a'16 } bes'2. | }
    { \voiceTwo <bes d'>1\p\arpeggio | <g bes d'>1\arpeggio | <d' bes'>1\arpeggio | <f a c'>1\arpeggio | a'1 | <d' ees' g'>1\arpeggio | <bes d' f'>1\arpeggio | <a c' ees' f'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <g bes d'>1\p\arpeggio | \acciaccatura { g,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 g4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 f4 | \acciaccatura { f,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g4 | \acciaccatura { f,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <ees f a c'>4\arpeggio f8 a8 c'8 f8 ees4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 a8 c'8 c4 | \acciaccatura { bes,,8 } <bes, d f g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
