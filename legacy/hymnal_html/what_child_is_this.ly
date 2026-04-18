\version "2.22.1"

\header {
  title = "284  What Child Is This?"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key e \minor
  \time 3/4
}

upper = {
  \global
  <<
    { \voiceOne e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } }\mf g'4 a'8 b'8. c''16 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 fis'8 d'8. e'16 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } g'4 e'8 e'8. ees'16 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } fis'4. b4 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 a'8 b'8. c''16 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 fis'8 d'8. e'16 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } g'8. fis'16 e'8 ees'8. cis'16 | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } e'4. e'4. | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } d''8. cis''16 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 fis'8 d'8. e'16 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } g'4 e'8 e'8. ees'16 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } } } fis'4 d'8 b4. | d''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } } } d''8. cis''16 | b'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 fis'8 d'8. e'16 | fis'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "2" } } } g'8. fis'16 e'8 ees'8. cis'16 | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" "7" } } } e'4. \acciaccatura { fis'16 d'16 } e'4 | }
    { \voiceTwo r2. | g'2. | <fis g b d'>2.\arpeggio | <c e g>2.\arpeggio | r2. | g'2. | <fis g b d'>2.\arpeggio | <c e g>2.\arpeggio | <e' g' b'>2.\arpeggio | g'2. | <fis g b d'>2.\arpeggio | <e fis a c'>2.\arpeggio | <e' fis' a' c''>2.\arpeggio | g'2. | <fis g b d'>2.\arpeggio | <g a c'>2.\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { e,8 } <c e g>2.\p\arpeggio | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 fis4 | \acciaccatura { e,8 } <g, b, c e>4\arpeggio b,8 c8 g,4 | \acciaccatura { b,,8 } <g, b, d>4\arpeggio b,8 d8 fis,4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 c4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 fis4 | \acciaccatura { e,8 } <g, b, c e>4\arpeggio b,8 c8 g,4 | \acciaccatura { b,,8 } <g, b, d>4\arpeggio b,8 d8 fis,4 | \acciaccatura { e,8 } <c e g>4\arpeggio e8 g8 c4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 fis4 | \acciaccatura { e,8 } <g, b, c e>4\arpeggio b,8 c8 g,4 | \acciaccatura { b,,8 } <fis, g, b, d>4\arpeggio g,8 b,8 c4 | \acciaccatura { b,,8 } <fis, g, b, d>4\arpeggio g,8 b,8 a,4 | \acciaccatura { g,,8 } <c e g>4\arpeggio e8 g8 fis4 | \acciaccatura { e,8 } <g, b, c e>4\arpeggio b,8 c8 c4 | \acciaccatura { b,,8 } <g, b, d fis>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
