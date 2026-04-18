\version "2.22.1"

\header {
  title = "206  Open Now Thy Gates of Beauty"
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
    { \voiceOne bes4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf c'8 d'4 bes4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } ees'4 f'4 f'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'8 g'8 f'4 d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 \acciaccatura { c''16 a'16 } bes'2 | bes4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c'8 d'4 bes4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } ees'4 f'4 f'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'8 g'8 f'4 d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 \acciaccatura { c''16 a'16 } bes'2 | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''8 c''4 c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } bes'4 a'2 | g'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 f'4 bes'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 \acciaccatura { c''16 a'16 } bes'2 | }
    { \voiceTwo <bes, d f>1\p\arpeggio | bes1 | <bes d'>1\arpeggio | <bes d' f'>1\arpeggio | <bes, d f>1\arpeggio | bes1 | <bes d'>1\arpeggio | <bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | <g bes d'>1\arpeggio | ees'1 | f'1 | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <g bes d'>1\p\arpeggio | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 a4 | \acciaccatura { g,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 c'4 | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 g4 | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 c'4 | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 a4 | \acciaccatura { g,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 c'4 | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 g4 | \acciaccatura { bes,,8 } <g bes d'>4\arpeggio bes8 d'8 bes8 d'8 a4 | \acciaccatura { g,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 d4 | \acciaccatura { c,8 } <c ees g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
