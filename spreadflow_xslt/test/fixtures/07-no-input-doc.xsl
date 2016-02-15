<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:param name="who" select="'world'"/>
  <xsl:template match="/">
    <greeting>Hello, <xsl:value-of select="$who"/>!</greeting>
  </xsl:template>
</xsl:stylesheet>
