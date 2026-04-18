\version "2.22.1"

\header {
  title = "277  We Gather Together"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } }\mf a'4. b'8 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } fis'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4. fis'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } fis'4 \acciaccatura { e'16 cis'16 } d'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4. b'8 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4. e''8 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4. a'8 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4. b'8 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 \acciaccatura { b'16 g'16 } a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4. b'8 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } a'8 fis'4 \acciaccatura { e'16 cis'16 } d'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4. a'8 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'8 a'4. g'8 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'8 g'4 e'4. | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } \acciaccatura { e'16 cis'16 } d'2 | }
    { \voiceTwo <cis' e' g'>2.\p\arpeggio | <cis' e'>2.\arpeggio | d'2. | <g a cis'>2.\arpeggio | <d' fis'>2.\arpeggio | <b d' fis'>2.\arpeggio | <b d' fis'>2.\arpeggio | <fis b d'>2.\arpeggio | <fis b d'>2.\arpeggio | <d' fis'>2.\arpeggio | <d' fis'>2.\arpeggio | <g a cis' e'>2.\arpeggio | <g b>2.\arpeggio | <g b d'>2.\arpeggio | <d fis a>2.\arpeggio | <a, b, d fis>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <d, fis, a, b,>2.\p\arpeggio | \acciaccatura { d,8 } <d, fis, a, b,>4\arpeggio fis,8 a,8 e,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 a,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis4 | \acciaccatura { b,,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 a,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 a,4 | \acciaccatura { d,8 } <d, fis, a,>4\arpeggio fis,8 a,8 a,4 | \acciaccatura { g,,8 } <d, fis, a,>4\arpeggio fis,8 a,8 e,4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis e g>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
