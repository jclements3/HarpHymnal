\version "2.22.1"

\header {
  title = "006  A Mighty Fortress Is Our God"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf d''4 d''4 a'8 b'8 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''8 cis''8 b'4 \acciaccatura { b'16 g'16 } a'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''4 b'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 fis'8 e'4 d'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 d''4 a'8 b'8 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''8 cis''8 b'4 a'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''4 b'4 \acciaccatura { b'16 g'16 } a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 fis'8 e'4 d'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } fis'4 a'4 \acciaccatura { cis''16 a'16 } b'4 | aes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 d'4 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } b'4 cis''4 \acciaccatura { e''16 cis''16 } d''4 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d''4 cis''4 b'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 b'4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'4 g'4 \acciaccatura { g'16 e'16 } fis'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } cis''4 b'4 a'4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'8 fis'8 e'4 \acciaccatura { e'16 cis'16 } d'4 | }
    { \voiceTwo <d' fis'>1\p\arpeggio | <b d' fis'>1\arpeggio | <d' fis'>1\arpeggio | a'1 | <d' fis'>1\arpeggio | <b d' fis'>1\arpeggio | <d' fis'>1\arpeggio | a'1 | cis'1 | <e g b>1\arpeggio | fis'1 | <fis' a'>1\arpeggio | <e' g'>1\arpeggio | d'1 | <g cis' e'>1\arpeggio | <g cis'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <a, cis e>1\p\arpeggio | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 a,4 | \acciaccatura { a,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 cis4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 b,4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <d, e, g, b,>4\arpeggio e,8 g,8 b,8 e,8 d,4 | \acciaccatura { e,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 d,4 | \acciaccatura { fis,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 fis,4 | \acciaccatura { e,8 } <d, fis, a,>4\arpeggio fis,8 a,8 fis,8 a,8 e,4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 b,4 | \acciaccatura { b,,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <b, d fis>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
