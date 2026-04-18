\version "2.22.1"

\header {
  title = "115  Immortal, Invisible, God Only Wise"
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
    { \voiceOne g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf e'4 c'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis'4 d'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { a'16 fis'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 c'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis'4 d'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } \acciaccatura { a'16 fis'16 } g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 b'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 \acciaccatura { a'16 fis'16 } g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'4 b'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 e'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } fis'4 d'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { a'16 fis'16 } g'2 | }
    { \voiceTwo a2.\p | <e g b>2.\arpeggio | e'2. | <c' d' fis'>2.\arpeggio | a2. | <e g b>2.\arpeggio | e'2. | <c' d' fis'>2.\arpeggio | <g b d'>2.\arpeggio | e'2. | e'2. | <b d' fis'>2.\arpeggio | <a c'>2.\arpeggio | <e g b>2.\arpeggio | e'2. | <b e'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { g,,8 } <g, b, d>2.\p\arpeggio | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 fis4 | \acciaccatura { e,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 d4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 fis4 | \acciaccatura { e,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis g b>4\arpeggio fis8 g8 d4 | \acciaccatura { g,,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 d4 | \acciaccatura { e,8 } <b, d fis>4\arpeggio d8 fis8 c4 | \acciaccatura { b,,8 } <g, b, d>4\arpeggio b,8 d8 a,4 | \acciaccatura { g,,8 } <g, b, d>4\arpeggio b,8 d8 b,4 | \acciaccatura { a,,8 } <a, c e>4\arpeggio c8 e8 fis4 | \acciaccatura { e,8 } <d fis a>4\arpeggio fis8 a8 e4 | \acciaccatura { d,8 } <d fis a>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
