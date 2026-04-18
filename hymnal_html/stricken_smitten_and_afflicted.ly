\version "2.22.1"

\header {
  title = "232  Stricken, Smitten, and Afflicted"
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
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } }\mf a'4 bes'2 bes'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 a'2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 g'2 a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis'4 \acciaccatura { a'16 f'16 } g'1 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 bes'2 bes'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 a'2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 g'2 a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'4 \acciaccatura { a'16 f'16 } g'1 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 d''2 d''2 | ees''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''4 c''2 c''2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } c''4 bes'2 \acciaccatura { c''16 a'16 } bes'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } bes'4 a'1 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } fis'4 g'2 \acciaccatura { c''16 a'16 } bes'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 a'2 a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 g'2 a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'4 \acciaccatura { a'16 f'16 } g'1 | }
    { \voiceTwo ees'1.\p | f'1. | <f a c'>1.\arpeggio | <ees g bes>1.\arpeggio | ees'1. | f'1. | <f a c'>1.\arpeggio | <g bes d'>1.\arpeggio | g'1. | <g' bes'>1.\arpeggio | <ees' g'>1.\arpeggio | <a bes d' f'>1.\arpeggio | ees'1. | <bes d' f'>1.\arpeggio | <f a c'>1.\arpeggio | <c f a>1.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <a, c ees>1.\p\arpeggio | \acciaccatura { c,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { a,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 a,4 | \acciaccatura { g,,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 d4 | \acciaccatura { c,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { a,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 ees4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 c4 | \acciaccatura { bes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 ees8 g8 d8 ees8 a,4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 c8 ees8 c8 ees8 bes,4 | \acciaccatura { a,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>1.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
