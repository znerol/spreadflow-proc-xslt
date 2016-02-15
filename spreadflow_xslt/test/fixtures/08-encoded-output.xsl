<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="utf-8"/>
  <xsl:param name="who" select="'world'"/>
  <xsl:template match="/">
    <xsl:text>Hello, </xsl:text><xsl:value-of select="$who"/><xsl:text>!</xsl:text>
  </xsl:template>
</xsl:stylesheet>
