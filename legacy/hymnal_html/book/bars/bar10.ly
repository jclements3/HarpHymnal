\version "2.22.1"
\header { tagline = ##f }
\paper {
  indent = 0\mm
  line-width = 42\mm
  ragged-right = ##f
  oddHeaderMarkup = ""
  evenHeaderMarkup = ""
  oddFooterMarkup = ""
  evenFooterMarkup = ""
  page-breaking = #ly:one-line-breaking
  system-system-spacing.basic-distance = #0
}

\score {
  \new PianoStaff \with { \remove "Bar_number_engraver" } <<
    \new Staff \with {
      \remove "Time_signature_engraver"
      instrumentName = ""
    } <<
      \new Voice { \voiceOne \clef treble \key bes \major bes'4. d''4. }
      \new Voice { \voiceTwo \key bes \major <ees' g'>2.\arpeggio }
    >>
    \new Staff \with {
      \remove "Time_signature_engraver"
    } { \clef bass \key bes \major \acciaccatura { bes,8 } <bes d' f'>2.\arpeggio }
  >>
  \layout {
    \context { \Score \remove "Bar_number_engraver" }
  }
}
