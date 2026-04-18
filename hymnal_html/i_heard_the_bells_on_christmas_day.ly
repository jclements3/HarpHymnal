\version "2.22.1"

\header {
  title = "106  I Heard The Bells On Christmas Day"
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
    { \voiceOne ees'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'4. fis'8 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } aes'4. g'8 aes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 ees''4 \acciaccatura { ees''16 c''16 } d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4. bes'8 bes'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4. aes'8 \acciaccatura { aes'16 f'16 } g'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4. f'8 ees'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 aes'4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'4. f'8 \acciaccatura { f'16 d'16 } ees'4 | }
    { \voiceTwo <ees g bes>1\p\arpeggio | <ees g bes>1\arpeggio | <ees' g'>1\arpeggio | <ees' g'>1\arpeggio | <g bes d'>1\arpeggio | <g bes d'>1\arpeggio | <bes d'>1\arpeggio | <g c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { ees,8 } <bes, d f>1\p\arpeggio | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 f,4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 c4 | \acciaccatura { c,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 f4 | \acciaccatura { ees,8 } <ees, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 ees,4 | \acciaccatura { g,,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 g,4 | \acciaccatura { f,8 } <f, aes, c>4\arpeggio aes,8 c8 aes,8 c8 c4 | \acciaccatura { bes,,8 } <bes, d f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
