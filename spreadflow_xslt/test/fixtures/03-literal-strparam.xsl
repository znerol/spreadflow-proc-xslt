<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/TR/xhtml1/strict">

<xsl:output method="xml" indent="yes" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<xsl:param name="extract_id"/>

<xsl:template match="sales">
    <xsl:apply-templates select="division[@id=$extract_id][1]"/>
</xsl:template>

<xsl:template match="division">
    <xsl:copy-of select="."/>
</xsl:template>

<xsl:template match="@*|node()">
    <xsl:message terminate = "yes">Unmatched element encountered</xsl:message>
</xsl:template>

</xsl:stylesheet>
