\version "2.22.1"

\header {
  title = "222  Savior Of The Nations Come"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf g'4 f'4 bes'4 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 a'4 \acciaccatura { a'16 f'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 c''4. bes'8 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 bes'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 d''4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'8 a'8 \acciaccatura { a'16 f'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 f'4 bes'4 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 a'4 \acciaccatura { a'16 f'16 } g'2 | }
    { \voiceTwo <f a c'>1\p\arpeggio | <f a c'>1\arpeggio | <g bes d'>1\arpeggio | <a c' ees'>1\arpeggio | <a c' ees'>1\arpeggio | <bes d' f'>1\arpeggio | <bes d'>1\arpeggio | <bes ees'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <ees g bes>1\p\arpeggio | \acciaccatura { a,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 d4 | \acciaccatura { c,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 a,4 | \acciaccatura { c,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 ees4 | \acciaccatura { d,8 } <d f a>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
