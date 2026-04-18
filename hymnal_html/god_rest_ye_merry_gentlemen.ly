\version "2.22.1"

\header {
  title = "079  God Rest Ye Merry Gentlemen"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key e \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } }\mf e'4 b'4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } g'4 fis'4 \acciaccatura { fis'16 d'16 } e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 fis'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } b'2. | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } e'4 b'4 \acciaccatura { c''16 a'16 } b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } g'4 fis'4 e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } e'4 fis'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } b'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } c''4 a'4 \acciaccatura { c''16 a'16 } b'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "ø7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } } } d''4 e''4 b'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 e'4 fis'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } a'2 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } b'2 c''4 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } b'4 a'4 g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } e'2 g'8 fis'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'2 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } b'4 c''4 \acciaccatura { e''16 c''16 } d''4 | e''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } b'4 a'4 g'4 | fis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" \raise #0.6 \smaller "2" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } \acciaccatura { fis'16 d'16 } e'2. | }
    { \voiceTwo <c' g'>1\p\arpeggio | <g a c'>1\arpeggio | <g b>1\arpeggio | <fis g b d'>1\arpeggio | <c' g'>1\arpeggio | <g a c'>1\arpeggio | <g b>1\arpeggio | <fis g b d'>1\arpeggio | <e' g'>1\arpeggio | <c' d' fis' a'>1\arpeggio | d'1 | <fis a c'>1\arpeggio | <d' fis'>1\arpeggio | e'1 | c'1 | c'1 | <fis' g'>1\arpeggio | <c' e'>1\arpeggio | <a d'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { e,8 } <g, b, d>1\p\arpeggio | \acciaccatura { b,,8 } <g, b, d fis>4\arpeggio b,8 d8 fis8 b,8 g,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 c4 | \acciaccatura { b,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 fis,4 | \acciaccatura { e,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 g,4 | \acciaccatura { b,,8 } <g, b, d fis>4\arpeggio b,8 d8 fis8 b,8 a,4 | \acciaccatura { g,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 c4 | \acciaccatura { b,,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 fis,4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { g,,8 } <d e g b>4\arpeggio e8 g8 b8 e8 g4 | \acciaccatura { fis,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 b,4 | \acciaccatura { a,,8 } <e, g, b,>4\arpeggio g,8 b,8 g,8 b,8 a,4 | \acciaccatura { g,,8 } <e, g, b, c>4\arpeggio g,8 b,8 c8 g,8 a,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 e8 g8 fis4 | \acciaccatura { e,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 fis,4 | \acciaccatura { a,,8 } <fis, a, c>4\arpeggio a,8 c8 a,8 c8 fis,4 | \acciaccatura { e,8 } <g, b, c e>4\arpeggio b,8 c8 e8 b,8 g,4 | \acciaccatura { b,,8 } <g, b, d>4\arpeggio b,8 d8 b,8 d8 fis,4 | \acciaccatura { e,8 } <c e g>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
