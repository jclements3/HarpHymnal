\version "2.22.1"

\header {
  title = "156  Lord, Enthroned in Heavenly Splendor"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \minor
  \time 6/4
}

upper = {
  \global
  <<
    { \voiceOne d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf d'4 g'2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } bes'4 bes'2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } bes'4 d''2 c''4 bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'4 \acciaccatura { a'16 f'16 } g'1 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } d'4 g'2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } bes'4 bes'2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } bes'4 d''2 c''4 bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'4 \acciaccatura { a'16 f'16 } g'1 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'4 bes'2 g'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } bes'4 c''2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 d''2 bes'4 \acciaccatura { ees''16 c''16 } d''4 | ees''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d''8 c''4 d''8 c''8 bes'4 c''8 bes'8 a'8 g'8 | d''1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 bes'4 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 bes'4 a'4 a'4 | \acciaccatura { a'16 f'16 } g'1.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo <ees g bes>1.\p\arpeggio | <ees' g'>1.\arpeggio | <ees' g'>1.\arpeggio | <ees g bes>1.\arpeggio | <ees g bes>1.\arpeggio | <ees' g'>1.\arpeggio | <ees' g'>1.\arpeggio | <ees g bes>1.\arpeggio | ees'1. | <bes c' ees' g'>1.\arpeggio | <a c' ees'>1.\arpeggio | <bes d' f'>1.\arpeggio | <ees' g'>1.\arpeggio | <c' f'>1.\arpeggio | <c f a>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <bes, d f>1.\p\arpeggio | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 a,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 a,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 bes,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 a,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 a,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 a,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 bes,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 ees4 | \acciaccatura { d,8 } <bes, d f a>4\arpeggio d8 f8 a8 d8 f8 a8 d8 f8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 bes,8 d8 bes,8 d8 g,4 | \acciaccatura { c,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 ees4 | \acciaccatura { d,8 } <d f a>4\arpeggio f8 a8 f8 a8 f8 a8 f8 a8 a,4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
