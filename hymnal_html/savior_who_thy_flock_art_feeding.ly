\version "2.22.1"

\header {
  title = "225  Savior, Who Thy Flock Art Feeding"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'4 a'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 c''2 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } d''4 \acciaccatura { d''16 bes'16 } c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 g'4 g'4 | a'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 c''4 a'8 bes'8 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''8 bes'8 a'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } f'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 a'4 g'4 | \acciaccatura { g'16 e'16 } f'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <f a c'>1\p\arpeggio | f'1 | <e' f'>1\arpeggio | <a c' e'>1\arpeggio | <a c' e'>1\arpeggio | <a c' e'>1\arpeggio | f'1 | <c' e'>1\arpeggio | <bes d' f'>1\arpeggio | <bes d'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <c e g>1\p\arpeggio | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 g,4 | \acciaccatura { f,8 } <f, g, bes, d>4\arpeggio g,8 bes,8 d8 g,8 f,4 | \acciaccatura { g,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 bes,4 | \acciaccatura { a,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 bes,4 | \acciaccatura { a,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 g,4 | \acciaccatura { f,8 } <f, a, c>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
