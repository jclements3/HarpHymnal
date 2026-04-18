\version "2.22.1"

\header {
  title = "251  The Lord's Prayer (new)"
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
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf bes'4 c''4 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 g'4 fis'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { bes'16 g'16 } a'2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'2 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 \acciaccatura { d''16 bes'16 } c''4 | bes'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'2 | \acciaccatura { a'16 f'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } bes'4 c''4 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } c''2 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 c''4 bes'4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } d'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'4 \acciaccatura { a'16 f'16 } g'2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } bes'4 a'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } fis'2 | \acciaccatura { a'16 f'16 } g'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } | }
    { \voiceTwo <g bes d'>1\p\arpeggio | <g' bes'>1\arpeggio | <c' f'>1\arpeggio | <c' f'>1\arpeggio | <c' f'>1\arpeggio | <c' f' a'>1\arpeggio | <c' f'>1\arpeggio | <ees g bes>1\arpeggio | <bes c' ees' g'>1\arpeggio | <f' a'>1\arpeggio | <bes d' f'>1\arpeggio | <a bes f'>1\arpeggio | <f a c'>1\arpeggio | f'1 | <c f a>1\arpeggio | <c f a>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <ees g bes>1\p\arpeggio | \acciaccatura { bes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <bes, d f a>4\arpeggio d8 f8 a8 d8 c4 | \acciaccatura { bes,,8 } <g, bes, d ees>4\arpeggio bes,8 d8 ees8 bes,8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 ees4 | \acciaccatura { d,8 } <bes, d ees g>4\arpeggio d8 ees8 g8 d8 a,4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 ees4 | \acciaccatura { a,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <ees g bes>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
