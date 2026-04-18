\version "2.22.1"

\header {
  title = "233  Take My Life And Let It Be"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key g \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf g'4 | fis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''4 | \acciaccatura { c''16 a'16 } b'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } b'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''4 a'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'8 a'8 | a'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vii" "°" } } } \acciaccatura { a'16 fis'16 } g'4 | fis'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'8 d'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } c''4 | \acciaccatura { c''16 a'16 } b'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 e''4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'4 | \acciaccatura { a'16 fis'16 } g'2.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } | }
    { \voiceTwo <g b d'>2.\p\arpeggio | <b, e g>2.\arpeggio | <c' d' fis' a'>2.\arpeggio | <fis a c' d'>2.\arpeggio | <fis' g'>2.\arpeggio | <fis' g' b'>2.\arpeggio | <g b d'>2.\arpeggio | <c' d' fis'>2.\arpeggio | <g b d'>2.\arpeggio | <fis a c'>2.\arpeggio | <c' d' fis' a'>2.\arpeggio | <fis g b d'>2.\arpeggio | <fis' g'>2.\arpeggio | r2. | <c' e'>2.\arpeggio | <c' e'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <d fis a>2.\p\arpeggio | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 a,4 | \acciaccatura { g,,8 } <g, b, d e>4\arpeggio b,8 d8 g,4 | \acciaccatura { g,,8 } <g, a, c e>4\arpeggio a,8 c8 b,4 | \acciaccatura { a,,8 } <g, a, c e>4\arpeggio a,8 c8 a,4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 d4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 a,4 | \acciaccatura { g,,8 } <fis a c'>4\arpeggio a8 c'8 fis4 | \acciaccatura { fis,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 a,4 | \acciaccatura { g,,8 } <g, a, c e>4\arpeggio a,8 c8 g,4 | \acciaccatura { g,,8 } <g, a, c e>4\arpeggio a,8 c8 b,4 | \acciaccatura { a,,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
