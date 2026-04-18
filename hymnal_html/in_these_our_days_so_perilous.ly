\version "2.22.1"

\header {
  title = "119  In These Our Days So Perilous"
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
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } }\mf g'4 g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "2" } } } g'4 bes'4 a'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { c''16 a'16 } bes'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } c''4 bes'4 c''4 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { ees''16 c''16 } d''2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''4 c''4 d''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''4 bes'4 a'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 \acciaccatura { g'16 ees'16 } f'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'4 c''4 g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 \acciaccatura { a'16 f'16 } g'2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } } } d''4 c''4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 bes'4 a'8 g'8 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'2 | \acciaccatura { a'16 f'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo <ees g bes>1\p\arpeggio | <d' ees'>1\arpeggio | <f a c'>1\arpeggio | <f' a'>1\arpeggio | <g' bes'>1\arpeggio | <g' bes'>1\arpeggio | <ees' g'>1\arpeggio | <ees g bes>1\arpeggio | ees'1 | <ees g bes>1\arpeggio | <c' d' f' a'>1\arpeggio | <c' f'>1\arpeggio | <c' f' a'>1\arpeggio | <c f a>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <a, c ees>1\p\arpeggio | \acciaccatura { c,8 } <ees g a c'>4\arpeggio g8 a8 c'8 g8 a4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { a,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 ees4 | \acciaccatura { d,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { d,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 f4 | \acciaccatura { ees,8 } <c ees g>4\arpeggio ees8 g8 ees8 g8 a,4 | \acciaccatura { g,,8 } <d f a>4\arpeggio f8 a8 f8 a8 d4 | \acciaccatura { g,,8 } <d f a>4\arpeggio f8 a8 f8 a8 a,4 | \acciaccatura { g,,8 } <d f a>4\arpeggio f8 a8 f8 a8 d4 | \acciaccatura { f,8 } <d ees g bes>4\arpeggio ees8 g8 bes8 ees8 a,4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
