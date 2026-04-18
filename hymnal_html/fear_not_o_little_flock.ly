\version "2.22.1"

\header {
  title = "069  Fear Not, O Little Flock"
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
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf g'4 g'4 | d''2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 \acciaccatura { bes'16 g'16 } a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes'4 a'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 \acciaccatura { bes'16 g'16 } a'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iiiii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 a'4 bes'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } \acciaccatura { g'16 ees'16 } f'2 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes'4 a'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { ees''16 c''16 } d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } bes'4 a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } bes'4 a'4 | bes'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 \acciaccatura { bes'16 g'16 } a'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } d''2 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } c''4 bes'4 c''4 | a'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { a'16 f'16 } g'2 | }
    { \voiceTwo <g bes d'>1\p\arpeggio | <bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | <f a c' d'>1\arpeggio | g'1 | <ees' g'>1\arpeggio | <f bes d'>1\arpeggio | <bes d' f'>1\arpeggio | <d f a>1\arpeggio | <f a c' d'>1\arpeggio | g'1 | <c' d' f'>1\arpeggio | <f a c' d'>1\arpeggio | <c' ees' g'>1\arpeggio | <bes d' f'>1\arpeggio | <d' f' a'>1\arpeggio | <f' a'>1\arpeggio | <bes ees'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <ees g bes>1\p\arpeggio | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 ees4 | \acciaccatura { d,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 g,4 | \acciaccatura { bes,,8 } <g, bes, d ees>4\arpeggio bes,8 d8 ees8 bes,8 c4 | \acciaccatura { bes,,8 } <ees g bes>4\arpeggio g8 bes8 g8 bes8 a4 | \acciaccatura { g,,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 a,4 | \acciaccatura { c,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 d4 | \acciaccatura { c,8 } <a, c ees>4\arpeggio c8 ees8 c8 ees8 ees4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <g, bes, d ees>4\arpeggio bes,8 d8 ees8 bes,8 c4 | \acciaccatura { bes,,8 } <d f a>4\arpeggio f8 a8 f8 a8 d4 | \acciaccatura { f,8 } <d f g bes>4\arpeggio f8 g8 bes8 f8 c4 | \acciaccatura { bes,,8 } <g, bes, d ees>4\arpeggio bes,8 d8 ees8 bes,8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 g,4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 ees4 | \acciaccatura { d,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 g4 | \acciaccatura { f,8 } <d f a>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
