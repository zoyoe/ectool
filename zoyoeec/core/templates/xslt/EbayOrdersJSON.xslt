<?xml version="1.0"?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:output method="text" encoding="utf-8" omit-xml-declaration="yes" indent="yes"/>
<xsl:template name="escapeTitle">
  <xsl:param name="pText" select="ebay:Item/ebay:Title"/>

  <xsl:if test="string-length($pText) >0">
   <xsl:value-of select=
    "substring-before(concat($pText, '&quot;'), '&quot;')"/>

   <xsl:if test="contains($pText, '&quot;')">
    <xsl:text>\"</xsl:text>

    <xsl:call-template name="escapeTitle">
      <xsl:with-param name="pText" select=
      "substring-after($pText, '&quot;')"/>
    </xsl:call-template>
   </xsl:if>
  </xsl:if>
</xsl:template>

<xsl:template match="/">
<xsl:for-each select="//ebay:OrderArray">[
 <xsl:for-each select="./ebay:Order"> 
   {"CHRG_CODE":"7C55",
    "CNBSGNEE_NAME":"<xsl:value-of select="ebay:ShippingAddress/ebay:Name"/>",
    "CNSGNEE_ADDR_LINE1":"<xsl:value-of select="ebay:ShippingAddress/ebay:Street1"/>",
    "CNSGNEE_SUBURB":"<xsl:value-of select="ebay:ShippingAddress/ebay:CityName"/>",
    "CNSGNEE_STATE_CODE":"<xsl:value-of select="ebay:ShippingAddress/ebay:StateOrProvince"/>",
    "CNSGNEE_STATE_PCODE":"<xsl:value-of select="ebay:ShippingAddress/ebay:PostalCode"/>",
    "CNSGNEE_CNTRY_CODE":"<xsl:value-of select="ebay:ShippingAddress/ebay:Country"/>",
    "CNSGNEE_PHONE_NBR":"<xsl:value-of select="ebay:ShippingAddress/ebay:Phone"/>",
    "DELIVY_INSTRN":{
       "order_id":"<xsl:value-of select="ebay:OrderID"/>",
       "transactions":[
       <xsl:for-each select="./ebay:TransactionArray/ebay:Transaction"> 
         {"sku":"<xsl:value-of select="ebay:Item/ebay:SKU"/>",
          "title":"<xsl:call-template name="escapeTitle"/>",
          "ebayid":"<xsl:value-of select="ebay:Item/ebay:ItemID"/>",
          "quantity":"<xsl:value-of select="ebay:QuantityPurchased"/>"}
         <xsl:if test="position() != last()"><xsl:text>,</xsl:text></xsl:if>
       </xsl:for-each>]
       },
    "IS_SHIPPED":<xsl:choose><xsl:when test="./ebay:ShippedTime">true</xsl:when><xsl:otherwise>false</xsl:otherwise></xsl:choose>,
    "CREATE_TIME":"<xsl:value-of select="ebay:CreatedTime"/>",
    "IS_SIGNTR_REQD":"True"}<xsl:if test="position() != last()"><xsl:text>,</xsl:text></xsl:if>
 </xsl:for-each>]
</xsl:for-each>
</xsl:template>
</xsl:stylesheet>
