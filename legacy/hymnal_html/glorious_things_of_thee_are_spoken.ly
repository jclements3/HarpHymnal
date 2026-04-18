\version "2.22.1"

\header {
  title = "076  Glorious Things of Thee are Spoken"
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
    { \voiceOne f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'8 a'4 g'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 g'8 e'8 \acciaccatura { g'16 e'16 } f'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "Vii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''4 bes'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'8 f'8 c''2 | f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'8 a'4 g'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 g'8 e'8 \acciaccatura { g'16 e'16 } f'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''4 bes'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'8 f'8 c''2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 g'8 e'8 \acciaccatura { d'16 bes16 } c'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } a'4 g'8 e'8 c'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } bes'4 a'4. a'8 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } bes'8 c''8 c''2 | f''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } e''8 d''4 \acciaccatura { d''16 bes'16 } c''4 | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''8 c''8 bes'8 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } a'8 bes'8 c''8 d''8 bes'8 g'8 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'8 g'8 \acciaccatura { g'16 e'16 } f'2 | }
    { \voiceTwo <f a c'>1\p\arpeggio | c'1 | <g c' e'>1\arpeggio | d'1 | d'1 | c'1 | <c' e' g'>1\arpeggio | <c' e'>1\arpeggio | r1 | <bes d' f'>1\arpeggio | <c' e' g'>1\arpeggio | <f' a'>1\arpeggio | <e' f' a'>1\arpeggio | <c' e' g'>1\arpeggio | <bes c' e'>1\arpeggio | <bes d'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <c e g>1\p\arpeggio | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 e4 | \acciaccatura { d,8 } <c e g>4\arpeggio e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d4 | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { bes,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 bes,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 c8 e8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 g,4 | \acciaccatura { f,8 } <f, a, bes, d>4\arpeggio a,8 bes,8 d8 a,8 f,4 | \acciaccatura { bes,,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 d4 | \acciaccatura { c,8 } <c e f a>4\arpeggio e8 f8 a8 e8 g,4 | \acciaccatura { f,8 } <f, a, c>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
