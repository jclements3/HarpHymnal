\version "2.22.1"

\header {
  title = "057  Come, Ye Disconsolate"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key c \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } }\mf e'4 c'4 | a'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 \acciaccatura { a'16 f'16 } g'2 | f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 a'4 b'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { a'16 f'16 } g'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } e'4 e'4 | f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } f'8 a'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4 f'4 | \acciaccatura { a'16 f'16 } g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 a'4 | g'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } f'8 \acciaccatura { f'16 d'16 } e'2 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } d''8 c''8 b'8 a'8 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e''4 e''4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'2 f'4 | e'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d'4. c'8 | \acciaccatura { d'16 b16 } c'1^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo b1\p | <f a c'>1\arpeggio | <f a c'>1\arpeggio | <b c' e'>1\arpeggio | <b, c e g>1\arpeggio | <g b d'>1\arpeggio | <c' e'>1\arpeggio | <c' e'>1\arpeggio | f'1 | c'1 | <a c' e'>1\arpeggio | <e g b>1\arpeggio | <c' e'>1\arpeggio | <c' e' g'>1\arpeggio | <b, d f g>1\arpeggio | <f a>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, e, f, a,>1\p\arpeggio | \acciaccatura { f,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 c,4 | \acciaccatura { f,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, f, a,>4\arpeggio e,8 f,8 a,8 e,8 c,4 | \acciaccatura { c,8 } <c, e, f, a,>4\arpeggio e,8 f,8 a,8 e,8 g,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <a, c e>4\arpeggio c8 e8 c8 e8 a,4 | \acciaccatura { a,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 f,4 | \acciaccatura { e,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 d,4 | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 d,4 | \acciaccatura { c,8 } <c, e, g,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
