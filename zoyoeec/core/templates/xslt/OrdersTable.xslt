<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ebay="urn:ebay:apis:eBLBaseComponents"
  xmlns:xs ="http://www.w3.org/2001/XMLSchema">
<xsl:template match="//ebay:OrderArray">
 <table id='orderlist' class='table'>
   <thead style="display:none">
    <th>CNSGMT_ID</th>
    <th>CONSIGNMENT_NUMBER</th>
    <th>POST_RG_TO_ACCT</th>
    <th>CHRG_CODE</th>
    <th>MERCHANT_CNSGNEE_CODE</th>
    <th>CNSGNEE_NAME</th>
    <th>CNSGNEE_BUS_NAME</th>
    <th>CNSGNEE_ADDR_LINE1</th>
    <th>CNSGNEE_ADDR_LINE2</th>
    <th>CNSGNEE_ADDR_LINE3</th>
    <th>CNSGNEE_ADDR_LINE4</th>
    <th>CNSGNEE_SUBURB</th>
    <th>CNSGNEE_STATE_CODE</th>
    <th>CNSGNEE_PCODE</th>
    <th>CNSGNEE_CNTRY_CODE</th>
    <th>CNSGNEE_PHONE_NBR</th>
    <th>IS_PHONE_PRNT_REQD</th>
    <th>CNSGNEE_FAX_NBR</th>
    <th>DELIVY_INSTRN</th>
    <th>IS_SIGNTR_REQD</th>
    <th>IS_PART_DELIVY</th>
    <th>U_CMNTS</th>
    <th>ADD_TO_ADDRESS_BOOK</th>
    <th>CTC_AMT</th>
    <th>XREF</th>
    <th>IS_REF_PRINT_REQD</th>
    <th>REF2</th>
    <th>IS_REF2_PRINT_REQD</th>
    <th>CHRG_BCK_ACCT</th>
    <th>IS_RECURRG_CNSGMT</th>
    <th>RTN_NAME</th>
   </thead>
   <tbody>
 <xsl:for-each select="./ebay:Order"> 
   <tr>
   <td>C</td><!-- CNSGMT_ID -->
   <td></td>
   <td></td><!-- ST_RG_TO_ACCT -->
   <td>S1</td>
   <td></td>
   <td><xsl:value-of select="ebay:ShippingAddress/ebay:Name"/></td> <!-- CNBSGNEE_NAME -->
   <td></td>
   <td><xsl:value-of select="ebay:ShippingAddress/ebay:Street1"/></td>
   <td></td><!-- ADDR2-->
   <td></td><!-- ADDR3-->
   <td></td><!-- ADDR4-->
   <td><xsl:value-of select="ebay:ShippingAddress/ebay:CityName"/></td>
   <td><xsl:value-of select="ebay:ShippingAddress/ebay:StateOrProvince"/></td>
<!-- M -->
   <td><xsl:value-of select="ebay:ShippingAddress/ebay:PostalCode"/></td>
   <td><xsl:value-of select="ebay:ShippingAddress/ebay:Country"/></td>
   <td><xsl:value-of select="ebay:ShippingAddress/ebay:Phone"/></td>
   <td></td><!-- RD-->
   <td></td><!-- RD-->
<!-- R -->
   <td><xsl:value-of select="ebay:OrderID"/>
     <xsl:for-each select="./ebay:TransactionArray/ebay:Transaction"> 
       ;
       <xsl:value-of select="ebay:Item/ebay:ItemID"/> * <xsl:value-of select="ebay:QuantityPurchased"/>
     </xsl:for-each>
   </td>
   <td>True</td>
   <td></td>
   <td></td>
   <td></td>
   <td></td>
<!-- X -->
   <td></td>
   <td></td>
   <td></td>
<!-- AA -->
   <td></td>
   <td></td>
   <td></td>
   <td></td>
   </tr>
 </xsl:for-each>
   </tbody>
 </table>
</xsl:template>
</xsl:stylesheet>
