\version "2.22.1"

\header {
  title = "042  Blest Be The Tie That Binds"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key c \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } }\mf e'8 f'8 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } \acciaccatura { a'16 f'16 } g'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''8 b'8 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'8 f'8 \acciaccatura { a'16 f'16 } g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'8 b'8 c''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } c''8 a'8 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } \acciaccatura { a'16 f'16 } g'2 | }
    { \voiceTwo <b c'>2.\p\arpeggio | <b c' e'>2.\arpeggio | <b c' e' g'>2.\arpeggio | <d' f'>2.\arpeggio | c'2. | <c' e'>2.\arpeggio | <g a c' e'>2.\arpeggio | <g a c' e'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { c,8 } <c, d, f, a,>2.\p\arpeggio | \acciaccatura { c,8 } <c, d, f, a,>4\arpeggio d,8 f,8 c,4 | \acciaccatura { c,8 } <c, d, f, a,>4\arpeggio d,8 f,8 e,4 | \acciaccatura { d,8 } <c, e, g,>4\arpeggio e,8 g,8 d,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 g,4 | \acciaccatura { c,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d f>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d f>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
