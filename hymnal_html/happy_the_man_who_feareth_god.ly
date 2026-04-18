\version "2.22.1"

\header {
  title = "086  Happy the Man Who Feareth God"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key a \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne d'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf a'4 a'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 b'8 d''4 cis''8 | d''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'4 b'4 a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } fis'8 e'4 \acciaccatura { e'16 cis'16 } d'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } a'4 g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } e'8 b'4 a'8 g'4 | fis'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'8 d''4 | d''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } cis''8 b'4 e''4 d''8 e''8 | e''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } d''16 cis''16 b'8 b'8 \acciaccatura { b'16 gis'16 } a'2 | }
    { \voiceTwo fis'1\p | d'1 | <d' fis' a'>1\arpeggio | <b d' fis'>1\arpeggio | <gis a cis'>1\arpeggio | <gis b d'>1\arpeggio | <gis b d'>1\arpeggio | gis'1 | <d' e' gis'>1\arpeggio | gis'1 | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { a,,8 } <a, cis e>1\p\arpeggio | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 e4 | \acciaccatura { d,8 } <b, d fis>4\arpeggio d8 fis8 d8 fis8 cis4 | \acciaccatura { b,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <a, cis d fis>4\arpeggio cis8 d8 fis8 cis8 a,4 | \acciaccatura { d,8 } <d fis a>4\arpeggio fis8 a8 fis8 a8 a4 | \acciaccatura { gis,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 a4 | \acciaccatura { gis,8 } <e gis b>4\arpeggio gis8 b8 gis8 b8 fis4 | \acciaccatura { e,8 } <e gis a cis'>4\arpeggio gis8 a8 cis'8 gis8 b,4 | \acciaccatura { a,,8 } <a, cis e fis>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
