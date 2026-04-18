\version "2.22.1"

\header {
  title = "103  I Am Jesus' Little Lamb"
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
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf c''4 a'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'4 \acciaccatura { f'16 d'16 } e'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } c''4 a'4 a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'4 \acciaccatura { f'16 d'16 } e'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''4 a'4 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''8 c''8 b'8 a'8 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''4 a'4 \acciaccatura { b'16 g'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''8 b''8 b'8 a'8 g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 a'4 \acciaccatura { a'16 f'16 } g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } e'4 d'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 a'4 d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } b'4 \acciaccatura { d''16 b'16 } c''2 | }
    { \voiceTwo <b d' f'>1\p\arpeggio | <b d'>1\arpeggio | <b d' f'>1\arpeggio | <b d'>1\arpeggio | <b c' e'>1\arpeggio | <d' f'>1\arpeggio | <b c' e'>1\arpeggio | <d' f'>1\arpeggio | f'1 | <b, d f g>1\arpeggio | <c' e'>1\arpeggio | <e' a'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, e, g, a,>1\p\arpeggio | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 c,4 | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 d,4 | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 c,4 | \acciaccatura { c,8 } <c, d, f, a,>4\arpeggio d,8 f,8 a,8 d,8 e,4 | \acciaccatura { d,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, d, f, a,>4\arpeggio d,8 f,8 a,8 d,8 c,4 | \acciaccatura { d,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 d,4 | \acciaccatura { c,8 } <c, e, g,>4\arpeggio e,8 g,8 e,8 g,8 c,4 | \acciaccatura { c,8 } <c, e, g, a,>4\arpeggio e,8 g,8 a,8 e,8 d,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 a,4 | \acciaccatura { g,,8 } <f, g, b, d>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
